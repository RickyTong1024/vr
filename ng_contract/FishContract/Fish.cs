using Neo.SmartContract.Framework;
using Neo.SmartContract.Framework.Services.Neo;
using System;
using System.ComponentModel;
using System.Data.SqlTypes;
using System.Linq.Expressions;
using System.Numerics;
using System.Runtime.Remoting.Messaging;
using Neo.SmartContract.Framework.Services.System;
using Helper = Neo.SmartContract.Framework.Helper;

namespace FishContract
{
    public class Fish : SmartContract
    {
        public delegate void deleTransfer(byte[] from, byte[] to, BigInteger value);
        [DisplayName("transfer")]
        public static event deleTransfer Transferred;

        public delegate void deleMine(BigInteger oid, BigInteger dig_num);
        [DisplayName("mine")]
        public static event deleMine Mined;

        public class TransferInfo
        {
            public byte[] from;
            public byte[] to;
            public BigInteger value;
        }

        //管理员账户，改成自己测试用的的
        private static readonly byte[] adminWallet = Helper.ToScriptHash("Aakssdq6o3aL1PysQ23DEXrEeutwEeJeKQ");
        private static readonly byte[] serverWallet = Helper.ToScriptHash("ASw5dpPUdtzCaRznCXNydZJBRDtJCPD8B7");

        public static string name()
        {
            return "Fish Coin";//名称
        }

        public static string symbol()
        {
            return "Fish";//简称
        }

        private const ulong factor = 100000000;//精度
        private const ulong adminCoin = 240000000 * factor;//总量
        private const ulong mineCoin = 60000000 * factor;//总量

        public static byte decimals()
        {
            return 8;
        }

        public static object Main(string method, object[] args)
        {
            var magicstr = "Fish-test";
            if (Runtime.Trigger == TriggerType.Verification)
            {
                return false;
            }
            else if (Runtime.Trigger == TriggerType.VerificationR)
            {
                return true;
            }
            else if (Runtime.Trigger == TriggerType.Application)
            {
                var callscript = ExecutionEngine.CallingScriptHash;

                if (method == "totalSupply")
                    return totalSupply();
                if (method == "totalMine")
                    return totalMine();
                if (method == "name")
                    return name();
                if (method == "symbol")
                    return symbol();
                if (method == "decimals")
                    return decimals();
                if (method == "deploy")
                {
                    if (!Runtime.CheckWitness(adminWallet))
                        return false;
                    byte[] total_supply = Storage.Get(Storage.CurrentContext, "totalSupply");
                    if (total_supply.Length != 0)
                        return false;
                    var keyAdminWallet = new byte[] {0x11}.Concat(adminWallet);
                    Storage.Put(Storage.CurrentContext, keyAdminWallet, adminCoin);
                    Storage.Put(Storage.CurrentContext, "totalSupply", adminCoin);
                    BigInteger nowtime = Blockchain.GetHeader(Blockchain.GetHeight()).Timestamp;
                    Storage.Put(Storage.CurrentContext, "lastMineTime", nowtime);
					Storage.Put(Storage.CurrentContext, "deploy", 1);

                    Transferred(null, adminWallet, adminCoin);
                }
                if (method == "balanceOf")
                {
                    if (args.Length != 1)
                        return 0;
                    byte[] who = (byte[]) args[0];
                    if (who.Length != 20)
                        return false;
                    return balanceOf(who);
                }

                if (method == "transfer")
                {
                    if (args.Length != 3)
                        return false;
                    byte[] from = (byte[]) args[0];
                    byte[] to = (byte[]) args[1];
                    if (from == to)
                        return true;
                    if (from.Length != 20 || to.Length != 20)
                        return false;
                    BigInteger value = (BigInteger) args[2];
                    if (!Runtime.CheckWitness(from))
                        return false;
                    if (ExecutionEngine.EntryScriptHash.AsBigInteger() != callscript.AsBigInteger())
                        return false;
                    if (!IsPayable(to))
                        return false;
                    return transfer(from, to, value);
                }

                if (method == "transfer_app")
                {
                    if (args.Length != 3)
                        return false;
                    byte[] from = (byte[]) args[0];
                    byte[] to = (byte[]) args[1];
                    BigInteger value = (BigInteger) args[2];

                    if (from.AsBigInteger() != callscript.AsBigInteger())
                        return false;
                    return transfer(from, to, value);
                }

                if (method == "getTxInfo")
                {
                    if (args.Length != 1)
                        return 0;
                    byte[] txid = (byte[]) args[0];
                    return getTxInfo(txid);
                }

                if (method == "mine")
                {
					BigInteger deploy = Storage.Get(Storage.CurrentContext, "deploy").AsBigInteger();
                    if (deploy != 1)
                        return false;
                    if (!Runtime.CheckWitness(adminWallet))
                        return false;
                    BigInteger nowtime = Blockchain.GetHeader(Blockchain.GetHeight()).Timestamp;
                    BigInteger lasttime = Storage.Get(Storage.CurrentContext, "lastMineTime").AsBigInteger();
                    Storage.Put(Storage.CurrentContext, "lastMineTime", nowtime);
                    BigInteger dig_coin = (nowtime - lasttime) * factor / 10;
                    BigInteger total_mine = Storage.Get(Storage.CurrentContext, "totalMine").AsBigInteger();
                    BigInteger remind_mine = mineCoin - total_mine;
                    if (dig_coin > remind_mine)
                    {
                        dig_coin = remind_mine;
                    }
                    if (dig_coin > 0)
                    {
                        var keyServerWallet = new byte[] { 0x11 }.Concat(serverWallet);
                        BigInteger server_value = Storage.Get(Storage.CurrentContext, keyServerWallet).AsBigInteger();
                        Storage.Put(Storage.CurrentContext, keyServerWallet, server_value + dig_coin);
                        Storage.Put(Storage.CurrentContext, "totalMine", total_mine + dig_coin);

                        Transferred(null, keyServerWallet, dig_coin);
                    }

                    BigInteger oid = _add_oid();
                    Mined(oid, dig_coin);
                    return dig_coin;
                }

                if (method == "refund")
                {
                    if (args.Length != 2)
                        return false;
                    byte[] who = (byte[])args[0];
                    if (who.Length != 20)
                        return false;
                    BigInteger value = (BigInteger)args[1];
                    if (!Runtime.CheckWitness(adminWallet))
                        return false;
                    return transfer(serverWallet, who, value);
                }

                #region 升级合约,耗费490,仅限管理员
                if (method == "upgrade")
                {
                    //不是管理员 不能操作
                    if (!Runtime.CheckWitness(adminWallet))
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
                    string name = "Fish";
                    string version = "1.0";
                    string author = "Fish";
                    string email = "0";
                    string description = "Fish";

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
                #endregion
            }

            return false;

        }

        private static object totalSupply()
        {
            return Storage.Get(Storage.CurrentContext, "totalSupply").AsBigInteger();
        }

        private static object totalMine()
        {
            return Storage.Get(Storage.CurrentContext, "totalMine").AsBigInteger();
        }

        private static bool transfer(byte[] from, byte[] to, BigInteger value)
        {
            if (value <= 0)
                return false;
            if (from == to)
                return true;
            if (from.Length > 0)
            {
                var keyFrom = new byte[] {0x11}.Concat(from);
                BigInteger from_value = Storage.Get(Storage.CurrentContext, keyFrom).AsBigInteger();
                if (from_value < value)
                    return false;
                if (from_value == value)
                    Storage.Delete(Storage.CurrentContext, keyFrom);
                else
                {
                    Storage.Put(Storage.CurrentContext, keyFrom, from_value - value);
                }
            }

            if (to.Length > 0)
            {
                var keyTo = new byte[] {0x11}.Concat(to);
                BigInteger to_value = Storage.Get(Storage.CurrentContext, keyTo).AsBigInteger();
                Storage.Put(Storage.CurrentContext, keyTo, to_value + value);
            }

            setTxInfo(from, to, value);
            Transferred(from, to, value);
            return true;
        }

        private static void setTxInfo(byte[] from, byte[] to, BigInteger value)
        {
            TransferInfo info = new TransferInfo();
            info.@from = from;
            info.to = to;
            info.value = value;
            byte[] txInfo = Helper.Serialize(info);
            var txid = (ExecutionEngine.ScriptContainer as Transaction).Hash;
            var keyTxid = new byte[] {0x13}.Concat(txid);
            Storage.Put(Storage.CurrentContext, keyTxid, txInfo);
        }

        private static object balanceOf(byte[] who)
        {
            var keyAddress = new byte[] {0x11}.Concat(who);
            return Storage.Get(Storage.CurrentContext, keyAddress).AsBigInteger();
        }

        private static TransferInfo getTxInfo(byte[] txid)
        {
            byte[] keyTxid=new byte[] {0x13}.Concat(txid);
            byte[] v = Storage.Get(Storage.CurrentContext, keyTxid);
            if (v.Length == 0)
                return null;
            return Helper.Deserialize(v) as TransferInfo;
        }

        public static bool IsPayable(byte[] to)
        {
            var c = Blockchain.GetContract(to);
            if (c.Equals(null))
                return true;
            return c.IsPayable;
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
    }
}
