const neo_tools = require("./neo_tools.js");

function run(argv) {
	if (argv[0] == "addr2hash") {
		console.log(neo_tools.addr2hash(argv[1]));
    }
	else if (argv[0] == "addr2hash_r") {
		console.log(neo_tools.addr2hash_r(argv[1]));
    }
	else if (argv[0] == "hash2addr") {
		console.log(neo_tools.hash2addr(argv[1]));
    }
	else if (argv[0] == "r_hash2addr") {
		console.log(neo_tools.r_hash2addr(argv[1]));
    }
	else if (argv[0] == "deploy") {
		neo_tools.deploy();
    }
	else if (argv[0] == "total_mine") {
		neo_tools.total_mine();
    }
	else if (argv[0] == "mine") {
		neo_tools.mine();
    }
	else if (argv[0] == "tx_info") {
		neo_tools.tx_info(argv[1]);
	}
	else if (argv[0] == "balance_of") {
		neo_tools.balance_of(argv[1]);
	}
	else if (argv[0] == "transfer") {
		neo_tools.transfer(argv[1], argv[2], argv[3]);
	}
}

async function main() {
	await neo_tools.init("admin");
	run(process.argv.slice(2));
}

main();