$(document).ready(function () {
    var es = document.getElementsByName("libao_reward");
    for (var i = 0; i < es.length; ++i) {
        var e = es[i];
        var s = e.innerHTML;
        var sss = "";
        var words = s.split(' ');
        var num = parseInt(words.length / 4);
        for (var j = 0; j < num; ++j) {
            var ss = "";
            if (words[j * 4] == "1")
            {
                ss = get_prop(words[j * 4 + 1], "t_resource") + "*" + words[j * 4 + 2];
            }
            else if (words[j * 4] == "2")
            {
                ss = get_prop(words[j * 4 + 1], "t_item") + "*" + words[j * 4 + 2];
            }
            sss += "[" + ss + "]";
        }
        e.innerHTML = sss;
    }
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

function get_prop(id, prop)
{
	var props = read_txt(prop);
	
    for (var i = 0; i < props.length; i++) {
		if (props[i][0] == id)
		{
			return props[i][1];
		}
	}
    return "";
}
