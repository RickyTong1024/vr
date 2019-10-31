const neo_tools = require("./neo_tools.js");

function run() {
	neo_tools.mine();
}

async function main() {
	await neo_tools.init("mine");
	run();
	setInterval(run, 30000);
}

main();