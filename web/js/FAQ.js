
////窗体滚动事件开始==================================================
//$(window).scroll(function(event) {
//headerInit();
//});
//
//function headerInit(){
//if($(this).scrollTop()>0){
//  $("header").addClass("fixed-header-on");
//}else{
//  $("header").removeClass("fixed-header-on");
//}
//}
//
//headerInit();
////窗体滚动事件结束==================================================
$(".faq .title").click(function(){
    $(this).siblings("p").slideToggle("fast");
 });