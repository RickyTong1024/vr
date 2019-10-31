const neo_tools = require("./neo_tools.js");

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function main() {
	await neo_tools.init("refund");
	while (1)
	{
		await neo_tools.refund_loop();
		await sleep(30);
	}
}

main();