using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Services.Neo;
using Neo.SmartContract.Framework.Services.System;
using Helper = Neo.SmartContract.Framework.Helper;

using System;
using System.ComponentModel;
using System.Numerics;

namespace AuctionContract
{
    /**
     * smart contract for Auction
     * @author Clyde
     */
    public class Auction : SmartContract
    {
        // NG合约hash
        [Appcall("4c403ebdc48d4d7abf7bf8141ec03368eb4eddac")]
        static extern object deleNgcall(string method, object[] arr);

        // SGAS合约hash
        [Appcall("74f2dc36a68fdc4682034178eb2220729231db76")]
        static extern object deleSgascall(string method, object[] arr);

        // the owner, super admin address
        public static readonly byte[] Admin = "Aakssdq6o3aL1PysQ23DEXrEeutwEeJeKQ".ToScriptHash();
        
        // min fee for one transaction
        private const ulong TX_MIN_FEE = 5000000;

        // In the auction 正在拍卖中的记录
        [Serializable]
        public class AuctionInfo
        {
            public byte[] owner;
            public uint sellTime;
            public BigInteger beginPrice;
            public BigInteger endPrice;
            public BigInteger duration;
        }

        // 拍卖成交记录
        public class AuctionRecord
        {
            public BigInteger dressId;
            public byte[] seller;
            public byte[] buyer;
            public BigInteger sellPrice;
            public BigInteger sellTime;
        }

        //notify 上架拍卖通知
        public delegate void deleAuction(BigInteger oid, byte[] owner, BigInteger dressId, BigInteger beginPrice, BigInteger endPrice, BigInteger duration, uint sellTime);
        [DisplayName("auction")]
        public static event deleAuction Auctioned;

        //notify 取消拍卖通知
        public delegate void deleCancelAuction(BigInteger oid, byte[] owner, BigInteger dressId);
        [DisplayName("cancelAuction")]
        public static event deleCancelAuction CancelAuctioned;

        //notify 购买通知
        public delegate void deleAuctionBuy(BigInteger oid, byte[] buyer, BigInteger dressId, BigInteger price, BigInteger fee, BigInteger nowtime);
        [DisplayName("auctionBuy")]
        public static event deleAuctionBuy AuctionBuy;

        /**
         * 存储增加的代币数量
         */
        private static void _addTotal(BigInteger count)
        {
            BigInteger total = Storage.Get(Storage.CurrentContext, "totalExchargeSgas").AsBigInteger();
            total += count;
            Storage.Put(Storage.CurrentContext, "totalExchargeSgas", total);
        }
        /**
         * 不包含收取的手续费在内，所有用户存在拍卖行中的代币
         */
        public static BigInteger totalExchargeSgas()
        {
            return Storage.Get(Storage.CurrentContext, "totalExchargeSgas").AsBigInteger();
        }


        /**
         * 存储减少的代币数总量
         */
        private static void _subTotal(BigInteger count)
        {
            BigInteger total = Storage.Get(Storage.CurrentContext, "totalExchargeSgas").AsBigInteger();
            total -= count;
            if (total > 0)
            {
                Storage.Put(Storage.CurrentContext, "totalExchargeSgas", total);
            }
            else
            {
                Storage.Delete(Storage.CurrentContext, "totalExchargeSgas");
            }
        }

        /**
         * 用户在拍卖所存储的代币
         */
        public static BigInteger balanceOf(byte[] address)
        {
            //2018/6/5 cwt 修补漏洞
            byte[] keytaddress = new byte[] { 0x11 }.Concat(address);
            return Storage.Get(Storage.CurrentContext, keytaddress).AsBigInteger();
        }

        /**
         * 该txid是否已经充值过
         */
        public static bool hasAlreadyCharged(byte[] txid)
        {
            //2018/6/5 cwt 修补漏洞
            byte[] keytxid = new byte[] { 0x11 }.Concat(txid);
            byte[] txinfo = Storage.Get(Storage.CurrentContext, keytxid);
            if (txinfo.Length > 0)
            {
                // 已经处理过了
                return false;
            }
            return true;
        }

        /**
         * 使用txid充值
         */
        public static bool rechargeToken(byte[] owner, byte[] txid)
        {
            if (owner.Length != 20)
            {
                Runtime.Log("Owner error!");
                return false;
            }

            //2018/6/5 cwt 修补漏洞
            byte[] keytxid = new byte[] { 0x11 }.Concat(txid);
            byte[] keytowner = new byte[] { 0x11 }.Concat(owner);

            byte[] txinfo = Storage.Get(Storage.CurrentContext, keytxid);
            if (txinfo.Length > 0)
            {
                // 已经处理过了
                return false;
            }


            // 查询交易记录
            object[] args = new object[1] { txid };
            object[] res = (object[])deleSgascall("getTxInfo", args);

            if (res.Length > 0)
            {
                byte[] from = (byte[])res[0];
                byte[] to = (byte[])res[1];
                BigInteger value = (BigInteger)res[2];

                if (from == owner)
                {
                    if (to == ExecutionEngine.ExecutingScriptHash)
                    {
                        // 标记为处理
                        Storage.Put(Storage.CurrentContext, keytxid, value);

                        BigInteger nMoney = 0;
                        byte[] ownerMoney = Storage.Get(Storage.CurrentContext, keytowner);
                        if (ownerMoney.Length > 0)
                        {
                            nMoney = ownerMoney.AsBigInteger();
                        }
                        nMoney += value;

                        _addTotal(value);

                        // 记账
                        Storage.Put(Storage.CurrentContext, keytowner, nMoney.AsByteArray());
                        return true;
                    }
                }
            }
            return false;
        }

        /**
         * 提币
         */
        public static bool drawToken(byte[] sender, BigInteger count)
        {
            //2018/6/5 cwt 修补漏洞
            byte[] keytsender = new byte[] { 0x11 }.Concat(sender);

            if (Runtime.CheckWitness(sender))
            {
                BigInteger nMoney = 0;
                byte[] ownerMoney = Storage.Get(Storage.CurrentContext, keytsender);
                if (ownerMoney.Length > 0)
                {
                    nMoney = ownerMoney.AsBigInteger();
                }
                if (count <= 0 || count > nMoney)
                {
                    // 全部提走
                    count = nMoney;
                }

                // 转账
                object[] args = new object[4] { ExecutionEngine.ExecutingScriptHash, sender, count, ExecutionEngine.ExecutingScriptHash };
                bool res = (bool)deleSgascall("transfer", args);
                if (!res)
                {
                    return false;
                }

                // 记账
                nMoney -= count;

                _subTotal(count);

                if (nMoney > 0)
                {
                    Storage.Put(Storage.CurrentContext, keytsender, nMoney.AsByteArray());
                }
                else
                {
                    Storage.Delete(Storage.CurrentContext, keytsender);
                }

                return true;
            }
            return false;
        }

        /**
         * 创建拍卖
         */
        public static bool startAuction(byte[] owner, BigInteger dressId, BigInteger beginPrice, BigInteger endPrice, BigInteger duration)
        {
            if (!Runtime.CheckWitness(owner))
            {
                return false;
            }
            if (beginPrice < 0 || endPrice < 0 || beginPrice < endPrice)
            {
                return false;
            }
            if (endPrice < TX_MIN_FEE)
            {
                // 结束价格不能低于最低手续费
                return false;
            }

            // 物品放在拍卖行
            object[] args = new object[3] { owner, ExecutionEngine.ExecutingScriptHash, dressId };
            bool res = (bool)deleNgcall("transfer_P2A", args);
            if (res)
            {
                var nowtime = Blockchain.GetHeader(Blockchain.GetHeight()).Timestamp;

                AuctionInfo info = new AuctionInfo();
                info.owner = owner;
                info.sellTime = nowtime;
                info.beginPrice = beginPrice;
                info.endPrice = endPrice;
                info.duration = duration;

                // 入库记录
                _putAuctionInfo(dressId.AsByteArray(), info);

                // notify
                BigInteger oid = _add_oid();
                Auctioned(oid, owner, dressId, beginPrice, endPrice, duration, nowtime);
                return true;
            }

            return false;
        }

        /**
         * 从拍卖场购买,将钱划入合约名下，将物品给买家
         */
        public static bool buyOnAuction(byte[] sender, BigInteger dressId)
        {
            if (!Runtime.CheckWitness(sender))
            {
                //没有签名
                return false;
            }

            object[] objInfo = _getAuctionInfo(dressId.AsByteArray());
            if (objInfo.Length > 0)
            {
                AuctionInfo info = (AuctionInfo)(object)objInfo;
                byte[] owner = info.owner;

                var nowtime = Blockchain.GetHeader(Blockchain.GetHeight()).Timestamp;
                var secondPass = nowtime - info.sellTime;
                //var secondPass = (nowtime - info.sellTime) / 1000;
                //2018/6/5 cwt 修补漏洞
                byte[] keytsender = new byte[] { 0x11 }.Concat(sender);
                byte[] keytowner = new byte[] { 0x11 }.Concat(owner);

                BigInteger senderMoney = Storage.Get(Storage.CurrentContext, keytsender).AsBigInteger();
                BigInteger curBuyPrice = computeCurrentPrice(info.beginPrice, info.endPrice, info.duration, secondPass);
                var fee = curBuyPrice * 50 / 1000;
                if (fee < TX_MIN_FEE)
                {
                    fee = TX_MIN_FEE;
                }
                if(curBuyPrice < fee)
                {
                    curBuyPrice = fee;
                }

                if (senderMoney < curBuyPrice)
                {
                    // 钱不够
                    return false;
                }


                // 转移物品
                object[] args = new object[3] { ExecutionEngine.ExecutingScriptHash, sender, dressId };
                bool res = (bool)deleNgcall("transfer_A2P", args);
                if (!res)
                {
                    return false;
                }

                // 扣钱
                Storage.Put(Storage.CurrentContext, keytsender, senderMoney - curBuyPrice);

                // 扣除手续费
                BigInteger sellPrice = curBuyPrice - fee;
                _subTotal(fee);

                // 钱记在卖家名下
                BigInteger nMoney = 0;
                byte[] salerMoney = Storage.Get(Storage.CurrentContext, keytowner);
                if (salerMoney.Length > 0)
                {
                    nMoney = salerMoney.AsBigInteger();
                }
                nMoney = nMoney + sellPrice;
                Storage.Put(Storage.CurrentContext, keytowner, nMoney);

                // 删除拍卖记录
                Storage.Delete(Storage.CurrentContext, dressId.AsByteArray());

                // notify
                BigInteger oid = _add_oid();
                AuctionBuy(oid, sender, dressId, curBuyPrice, fee, nowtime);
                return true;
                
            }
            return false;
        }

        /**
         * 取消拍卖
         */
        public static bool cancelAuction(byte[] sender, BigInteger dressId)
        {
            object[] objInfo = _getAuctionInfo(dressId.AsByteArray());
            if (objInfo.Length > 0)
            {
                AuctionInfo info = (AuctionInfo)(object)objInfo;
                byte[] owner = info.owner;

                if (sender != owner)
                {
                    return false;
                }

                if (Runtime.CheckWitness(sender))
                {
                    object[] args = new object[3] { ExecutionEngine.ExecutingScriptHash, owner, dressId };
                    bool res = (bool)deleNgcall("transfer_A2P", args);
                    if (res)
                    {
                        Storage.Delete(Storage.CurrentContext, dressId.AsByteArray());
                        // notify
                        BigInteger oid = _add_oid();
                        CancelAuctioned(oid, owner, dressId);
                        return true;
                    }
                }
            }
            return false;
        }

        /**
         * 获取拍卖信息
         */
        public static AuctionInfo getAuctionById(BigInteger dressId)
        {
            object[] objInfo = _getAuctionInfo(dressId.AsByteArray());
            AuctionInfo info = (AuctionInfo)(object)objInfo;

            return info;
        }

        /**
         * 将收入提款到合约拥有者
         */
        public static bool drawToContractOwner(BigInteger count)
        {
            if (Runtime.CheckWitness(Admin))
            {
                BigInteger nMoney = 0;
                // 查询余额
                object[] args = new object[1] { ExecutionEngine.ExecutingScriptHash };
                BigInteger totalMoney = (BigInteger)deleSgascall("balanceOf", args);
                BigInteger supplyMoney = Storage.Get(Storage.CurrentContext, "totalExchargeSgas").AsBigInteger();

                BigInteger canDrawMax = totalMoney - supplyMoney;
                if (count <= 0 || count > canDrawMax)
                {
                    // 全部提走
                    count = canDrawMax;
                }

                // 转账
                args = new object[3] { ExecutionEngine.ExecutingScriptHash, Admin, count };
                bool res = (bool)deleSgascall("transfer_app", args);
                if (!res)
                {
                    return false;
                }

                // 记账
                _subTotal(count);
                return true;
            }
            return false;
        }

        /**
         * 合约入口
         */
        public static Object Main(string method, params object[] args)
        {
            if (Runtime.Trigger == TriggerType.Verification) //取钱才会涉及这里
            {
                if (Admin.Length == 20)
                {
                    // if param ContractOwner is script hash
                    //return Runtime.CheckWitness(ContractOwner);
                    return false;
                }
                else if (Admin.Length == 33)
                {
                    // if param ContractOwner is public key
                    byte[] signature = method.AsByteArray();
                    return VerifySignature(signature, Admin);
                }
            }
            else if (Runtime.Trigger == TriggerType.VerificationR)
            {
                return true;
            }
            else if (Runtime.Trigger == TriggerType.Application)
            {
                //必须在入口函数取得callscript，调用脚本的函数，也会导致执行栈变化，再取callscript就晚了
                var callscript = ExecutionEngine.CallingScriptHash;
                //this is in nep5
                if (method == "totalExchargeSgas") return totalExchargeSgas();
                if (method == "balanceOf")
                {
                    if (args.Length != 1)
                        return false;
                    byte[] account = (byte[])args[0];
                    return balanceOf(account);
                }
                if (method == "startAuction")
                {
                    if (args.Length != 5)
                        return false;
                    byte[] owner = (byte[])args[0];
                    BigInteger dressId = (BigInteger)args[1];
                    BigInteger beginPrice = (BigInteger)args[2];
                    BigInteger endPrice = (BigInteger)args[3];
                    BigInteger duration = (BigInteger)args[4];

                    return startAuction(owner, dressId, beginPrice, endPrice, duration);
                }
                if (method == "buyOnAuction")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] owner = (byte[])args[0];
                    BigInteger dressId = (BigInteger)args[1];

                    return buyOnAuction(owner, dressId);
                }
                if (method == "cancelAuction")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] owner = (byte[])args[0];
                    BigInteger dressId = (BigInteger)args[1];

                    return cancelAuction(owner, dressId);
                }
                if (method == "getAuctionById")
                {
                    if (args.Length != 1)
                        return false;
                    BigInteger dressId = (BigInteger)args[0];

                    return getAuctionById(dressId);
                }
                if (method == "drawToken")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] owner = (byte[])args[0];
                    BigInteger count = (BigInteger)args[1];

                    return drawToken(owner, count);
                }
                if (method == "drawToContractOwner")
                {
                    if (args.Length != 1)
                        return false;
                    BigInteger count = (BigInteger)args[0];

                    return drawToContractOwner(count);
                }
                if (method == "rechargeToken")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] owner = (byte[])args[0];
                    byte[] txid = (byte[])args[1];

                    return rechargeToken(owner, txid);
                }
                if (method == "hasAlreadyCharged")
                {
                    if (args.Length != 1)
                        return false;
                    byte[] txid = (byte[])args[0];

                    return hasAlreadyCharged(txid);
                }
                if (method == "getAuctionRecord")
                {
                    if (args.Length != 1)
                        return false;
                    byte[] txid = (byte[])args[0];
                    return getAuctionRecord(txid);
                }
                if (method == "upgrade")//合约的升级就是在合约中要添加这段代码来实现
                {
                    //不是管理员 不能操作
                    if (!Runtime.CheckWitness(Admin))
                        return false;

                    if (args.Length != 1 && args.Length != 9)
                        return false;

                    byte[] script = Blockchain.GetContract(ExecutionEngine.ExecutingScriptHash).Script;
                    byte[] new_script = (byte[])args[0];
                    //如果传入的脚本一样 不继续操作
                    if (script == new_script)
                        return false;

                    byte[] parameter_list = new byte[] { 0x07, 0x10 };
                    byte return_type = 0x05;
                    bool need_storage = (bool)(object)05;
                    string name = "Auction";
                    string version = "1.1";
                    string author = "CG";
                    string email = "0";
                    string description = "test";

                    if (args.Length == 9)
                    {
                        parameter_list = (byte[])args[1];
                        return_type = (byte)args[2];
                        need_storage = (bool)args[3];
                        name = (string)args[4];
                        version = (string)args[5];
                        author = (string)args[6];
                        email = (string)args[7];
                        description = (string)args[8];
                    }
                    Contract.Migrate(new_script, parameter_list, return_type, need_storage, name, version, author, email, description);
                    return true;
                }
            }
            return false;
        }

        /**
        * 操作id保证顺序
        */
        private static BigInteger _add_oid()
        {
            BigInteger oid = Storage.Get(Storage.CurrentContext, "oid").AsBigInteger();
            Storage.Put(Storage.CurrentContext, "oid", oid + 1);
            return oid;
        }
        /**
		 * Computes the current price of an auction.
		 * @param startingPrice
		 * @param endingPrice
		 * @param duration
		 * @param secondsPassed
		 * @return 
		 */
        private static BigInteger computeCurrentPrice(BigInteger beginPrice, BigInteger endingPrice, BigInteger duration, BigInteger secondsPassed)
        {
            if (duration < 1)
            {
                // 避免被0除
                duration = 1;
            }

            if (secondsPassed >= duration)
            {
                return endingPrice;
            }
            else
            {
                return beginPrice + (endingPrice - beginPrice) * secondsPassed / duration;
            }
        }

        /**
         * 获取拍卖信息
         */
        private static object[] _getAuctionInfo(byte[] dressId)
        {

            byte[] v = Storage.Get(Storage.CurrentContext, dressId);
            if (v.Length == 0)
                return new object[0];
            
            return (object[])Helper.Deserialize(v);
        }

        /**
         * 存储拍卖信息
         */
        private static void _putAuctionInfo(byte[] dressId, AuctionInfo info)
        {
            byte[] auctionInfo = Helper.Serialize(info);
            Storage.Put(Storage.CurrentContext, dressId, auctionInfo);
        }

        /**
         * 获取拍卖成交记录
         */
        public static object[] getAuctionRecord(byte[] dressId)
        {
            var key = "buy".AsByteArray().Concat(dressId);
            byte[] v = Storage.Get(Storage.CurrentContext, key);
            if (v.Length == 0)
            {
                return new object[0];
            }
            
            return (object[])Helper.Deserialize(v);
        }

        /**
         * 存储拍卖成交记录
         */
        private static void _putAuctionRecord(byte[] dressId, AuctionRecord info)
        {
            byte[] txInfo = Helper.Serialize(info);

            var key = "buy".AsByteArray().Concat(dressId);
            Storage.Put(Storage.CurrentContext, key, txInfo);
        }
    }
}
