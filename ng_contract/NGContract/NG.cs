using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Services.Neo;
using Neo.SmartContract.Framework.Services.System;
using Helper = Neo.SmartContract.Framework.Helper;

using System;
using System.ComponentModel;
using System.Numerics;


namespace NGContract
{
    /**
     * smart contract for Gladiator
     * @author Clyde
     */
    public class NG : SmartContract
    {
        /**
         * 时装属性结构数据
         */
        [Serializable]
        public class DressInfo
        {
            public byte[] owner;
            public byte type;
        }

        /**
         * 时装交易记录
         */
        public class TransferInfo
        {
            public byte[] from;
            public byte[] to;
            public BigInteger value;
        }

        // notify 转账通知
        public delegate void deleTransfer(BigInteger oid, byte[] from, byte[] to, BigInteger value);
        [DisplayName("transfer")]
        public static event deleTransfer Transferred;

        // notify 新的时装发布通知
        public delegate void deleCreate(BigInteger oid, BigInteger dressId, byte[] owner, int type);
        [DisplayName("create")]
        public static event deleCreate Created;

        // 合约拥有者，超级管理员
        public static readonly byte[] Admin = "Aakssdq6o3aL1PysQ23DEXrEeutwEeJeKQ".ToScriptHash();

        // 时装发行总量
        private const ulong ALL_SUPPLY_CG = 4000;

        /**
         * 获取时装拥有者
         */
        public static byte[] ownerOf(BigInteger dressId)
        {
            object[] objInfo = _getDressInfo(dressId.AsByteArray());
            DressInfo info = (DressInfo)(object) objInfo;
            if (info.owner.Length > 0)
            {
                return info.owner;
            }
            else
            {
                return new byte[] { };
            }
        }

        /**
          * 已经发行的时装总数
          */
        public static BigInteger totalSupply()
        {
            return Storage.Get(Storage.CurrentContext, "totalSupply").AsBigInteger();
        }

        /**
         * 生成新的时装数据，并记录
         */
        public static BigInteger createDress(byte[] tokenOwner, byte type)
        {
            if (tokenOwner.Length != 20)
            {
                return 0;
            }

            //
            if (Runtime.CheckWitness(Admin))
            {
                //判断下是否超过总量
                byte[] totalSupply = Storage.Get(Storage.CurrentContext, "totalSupply");
                if (totalSupply.AsBigInteger() >= ALL_SUPPLY_CG)
                {
                    return 0;
                }
                BigInteger newTotalSupply = totalSupply.AsBigInteger() + 1;
                totalSupply = newTotalSupply.AsByteArray();

                DressInfo newInfo = new DressInfo();
                newInfo.owner = tokenOwner;
                newInfo.type = type;

                _putDressInfo(totalSupply, newInfo);

                Storage.Put(Storage.CurrentContext, "totalSupply", totalSupply);

                // notify
                BigInteger oid = _add_oid();
                Created(oid, totalSupply.AsBigInteger(), newInfo.owner, newInfo.type);
                return totalSupply.AsBigInteger();
            }
            else
            {
                Runtime.Log("Only the contract owner may mint new tokens.");
                return 0;
            }
        }

        /**
         * 将时装资产转账给其他人
         */
        public static bool transfer(byte[] from, byte[] to, BigInteger dressId)
        {
            if (from.Length != 20 || to.Length != 20)
            {
                return false;
            }

            StorageContext ctx = Storage.CurrentContext;

            if (from == to)
            {
                //Runtime.Log("Transfer to self!");
                return true;
            }

            object[] objInfo = _getDressInfo(dressId.AsByteArray());
            if(objInfo.Length == 0)
            {
                return false;
            }

            DressInfo info = (DressInfo)(object)objInfo;
            byte[] ownedBy = info.owner;

            if (from != ownedBy)
            {
                //Runtime.Log("Token is not owned by tx sender");
                return false;
            }

            info.owner = to;
            _putDressInfo(dressId.AsByteArray(), info);

            //记录交易信息
            _setTxInfo(from, to, dressId);

            BigInteger oid = _add_oid();
            Transferred(oid, from, to, dressId);
            return true;

        }

        /**
         * 获取时装信息
         */
        public static DressInfo dressData(BigInteger dressId)
        {
            object[] objInfo = _getDressInfo(dressId.AsByteArray());
            DressInfo info = (DressInfo)(object)objInfo;
            return info;
        }

        /**
         * 获取交易信息
         */
        public static object[] getTXInfo(byte[] txid)
        {
            byte[] v = Storage.Get(Storage.CurrentContext, txid);
            if (v.Length == 0)
                return new object[0];

            return (object[])Helper.Deserialize(v);
        }

        /**
         * 合约入口
         */
        public static Object Main(string method, params object[] args)
        {
            if (Runtime.Trigger == TriggerType.Verification)
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

                if (method == "init")
                {
                    if (args.Length != 1)
                        return false;
                    if (Runtime.CheckWitness(Admin))
                    {
                        Storage.Put(Storage.CurrentContext, "auction", (byte[])args[0]);
                        Storage.Put(Storage.CurrentContext, "totalSupply", 0);
                        Storage.Put(Storage.CurrentContext, "oid", 0);
                        return true;
                    }
                }
                if (method == "view_init_auction")
                {
                    byte[] auction = Storage.Get(Storage.CurrentContext, "auction");
                    return auction;
                }
                if (method == "totalSupply") return totalSupply();

                if (method == "hasExtraData") return false;
                if (method == "isEnumable") return false;
                if (method == "hasBroker") return false;

                if (method == "ownerOf")
                {
                    if (args.Length != 1)
                        return false;
                    BigInteger dressId = (BigInteger)args[0];
                    return ownerOf(dressId);
                }
                if (method == "transfer_P2A")
                {
                    if (args.Length != 3)
                        return false;

                    byte[] from = (byte[])args[0];
                    byte[] to = (byte[])args[1];
                    BigInteger dressId = (BigInteger)args[2];

                    byte[] auction = Storage.Get(Storage.CurrentContext, "auction");
                    if (callscript.AsBigInteger() != auction.AsBigInteger())
                    {
                        return false;
                    }
                    return transfer(from, to, dressId);
                }
                if (method == "transfer_A2P")
                {
                    if (args.Length != 3)
                        return false;

                    byte[] from = (byte[])args[0];
                    byte[] to = (byte[])args[1];
                    BigInteger tokenId = (BigInteger)args[2];

                    byte[] auction = Storage.Get(Storage.CurrentContext, "auction");
                    if (callscript.AsBigInteger() != auction.AsBigInteger())
                    {
                        return false;
                    }

                    return transfer(from, to, tokenId);
                }
                if (method == "transfer")
                {
                    if (args.Length != 3)
                        return false;
                    byte[] from = (byte[])args[0];
                    byte[] to = (byte[])args[1];
                    BigInteger dressId = (BigInteger)args[2];

                    //没有from签名，不让转
                    if (!Runtime.CheckWitness(from))
                    {
                        return false;
                    }
                    //如果有跳板调用，不让转
                    if (ExecutionEngine.EntryScriptHash.AsBigInteger() != callscript.AsBigInteger())
                    {
                        return false;
                    }
                    return transfer(from, to, dressId);
                }
                if (method == "createDress")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] owner = (byte[])args[0];
                    byte type = (byte)args[1];

                    return createDress(owner, type);
                }
                if (method == "dressData")
                {
                    if (args.Length != 1)
                        return false;
                    BigInteger dressId = (BigInteger)args[0];
                    return dressData(dressId);
                }
                if (method == "getTXInfo")
                {
                    if (args.Length != 1)
                        return false;
                    byte[] txid = (byte[])args[0];
                    return getTXInfo(txid);
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
                    string name = "NeoGirl";
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
         * 获取时装结构
         */
        private static object[] _getDressInfo(byte[] dressId)
        {
            byte[] v = Storage.Get(Storage.CurrentContext, dressId);
            if (v.Length == 0)
                return new object[0];
            return (object[])Helper.Deserialize(v);
        }

        /**
         * 存储时装信息
         */
        private static void _putDressInfo(byte[] dressId, DressInfo info)
        {
            byte[] DressInfo = Helper.Serialize(info);
            Storage.Put(Storage.CurrentContext, dressId, DressInfo);
        }

        /**
         * 存储交易信息
         */
        private static void _setTxInfo(byte[] from, byte[] to, BigInteger value)
        {
            TransferInfo info = new TransferInfo();
            info.from = from;
            info.to = to;
            info.value = value;

            byte[] txinfo = Helper.Serialize(info);
            byte[] txid = (ExecutionEngine.ScriptContainer as Transaction).Hash;
            Storage.Put(Storage.CurrentContext, txid, txinfo);
        }
    }
}
