$(document).ready(function () {
    $("#id_reward1_1").change(function () {
        $("#id_reward1_2").empty();
        var v = $("#id_reward1_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_reward1_2");
        }
        else if (v == 2) {
            set_item("#id_reward1_2");
        }
    });

    $("#id_reward2_1").change(function () {
        $("#id_reward2_2").empty();
        var v = $("#id_reward2_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_reward2_2");
        }
        else if (v == 2) {
            set_item("#id_reward2_2");
        }
        else {
            set_sort("#id_reward2_2");
        }
    });

    $("#id_reward3_1").change(function () {
        $("#id_reward3_2").empty();
        var v = $("#id_reward3_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_reward3_2");
        }
        else if (v == 2) {
            set_item("#id_reward3_2");
        }
        else {
            set_sort("#id_reward2_2");
        }
    });

    $("#id_reward4_1").change(function () {
        $("#id_reward4_2").empty();
        var v = $("#id_reward4_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_reward4_2");
        }
        else if (v == 2) {
            set_item("#id_reward4_2");
        }
        else {
            set_sort("#id_reward2_2");
        }
    });

    $("#id_duihuan1_1").change(function () {
        $("#id_duihuan1_2").empty();
        var v = $("#id_duihuan1_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_duihuan1_2");
        }
        else if (v == 2) {
            set_item("#id_duihuan1_2");
        }
        else {
            set_sort("#id_reward2_2");
        }
    });

    $("#id_duihuan2_1").change(function () {
        $("#id_duihuan2_2").empty();
        var v = $("#id_duihuan2_1").val();
        if (v == 0) {
            return;
        }
        else if (v == 1) {
            set_ziyuan("#id_duihuan2_2");
        }
        else if (v == 2) {
            set_item("#id_duihuan2_2");
        }
        else {
            set_sort("#id_reward2_2");
        }
    });
});

function read_txt(name)
{
	var sorts = [];
    htmlobj = $.ajax({ url: "/static/other/" + name + ".txt?4", async: false });
    var text = htmlobj.responseText;
    var x = 0;
    var y = 0;
    var index1 = 0;
    var index2 = 0;
    var s;
	var txts = [];
	var txt = [];
    for (var i = 0; i < text.length; i++) {
        if (text.charAt(i) == '\r' || text.charAt(i) == '\t') {
            index1 = index2;
            index2 = i + 1;
            if (y > 1) {
                s = text.substring(index1, index2 - 1);
				txt.push(s);
            }
        }
        if (text.charAt(i) == '\n') {
            x = 0;
			y++;
			index1 = i + 1;
			index2 = i + 1;
			if (txt.length > 0)
			{
				txts.push(txt);
				txt = [];
			}
        }
        if (text.charAt(i) == '\t') {
            x++;
        }
    }
	return txts;
}

function add_sort(items)
{
    var sorts = read_txt("t_sort");
	
	var new_items = [];
	for (var i = 0; i < sorts.length; i++) {
		for (var j = 0; j < items.length; j++) {
			if (items[j][0] == sorts[i][0])
			{
				new_items.push(items[j]);
				break;
			}
		}
	}
	new_items = new_items.concat(items)
    return new_items;
}

function set_ziyuan(name)
{
	var resources = read_txt("t_resource");
	
    resources = add_sort(resources);

    for (var i = 0; i < resources.length; i++) {
        s1 = resources[i][0];
        s2 = s1 + "." + resources[i][1];
        var option = $("<option>").val(parseInt(s1)).text(s2);
        $(name).append(option);
    }
}

function set_item(name)
{
	var items = read_txt("t_item");
	
    items = add_sort(items);

    for (var i = 0; i < items.length; i++) {
        s1 = items[i][0];
        s2 = s1 + "." + items[i][1];
        var option = $("<option>").val(parseInt(s1)).text(s2);
        $(name).append(option);
    }
}
