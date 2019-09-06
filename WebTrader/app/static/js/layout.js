$(function () {
    // 登录页
    $('.login-main-bit i').on('click', function(){
        console.log(2);
        $('.login-main-bit input').val('');
    });

    // 通用侧边栏
    $('.page-sidebar-list h6').each(function (index) { 
        var that = $(this);
        var addname = 'page-sidebar-' + index;
        that.parent().addClass(addname);
        if(that.siblings().size() !== 0){
            that.parent().addClass('page-sidebar-special');
        }
    });

    $('.page-sidebar-special h6 a').on('click', function(){
        var that = $(this).parents('li');
        that.addClass('cur').siblings().removeClass('cur');
    });

    // 查询结果
    $('.query-results-menu dt').on('click', function(){
        $(this).parent().addClass('cur').siblings().removeClass('cur');
    });

    // 程序化交易
    $('.programmed-trading-left').on('click', function(){
        var that = $(this).find('.commoncaret-ascending');
        if(that.hasClass('cur')){
            that.removeClass('cur').siblings().addClass('cur');
        }else{
            that.addClass('cur').siblings().removeClass('cur');
        }
    });

    // 自动交易
    $('.manual-trading-title i').on('click', function(){
        var that = $(this);
        var num = $('.manual-trading-title input').val();
        if(that.hasClass('manual-trading-add')){
            num = num * 1 + 1;
        }else if(that.hasClass('manual-trading-subtract')){
            num = num * 1 - 1;
        }
        return $('.manual-trading-title input').val(num);
    });

    $('.manual-trading-table th').on('click', function(){
        var that = $(this).find('.commoncaret-ascending');
        if(that.hasClass('cur')){
            that.removeClass('cur').siblings().addClass('cur');
        }else{
            that.addClass('cur').siblings().removeClass('cur')
                .parents('th').siblings().find('.cur').removeClass('cur');
        }
    });

    $('.manual-trading-switch button').on('click', function(){
        var that = $(this);
        var index = that.index();
        that.addClass('cur').siblings().removeClass('cur')
            .parent().next().find('.manual-trading-bottom').eq(index).addClass('cur')
            .siblings().removeClass('cur');
    });

    // 通用分页器
    if(typeof layui != 'undefined') {
        var laypage = layui.laypage;
        laypage.render({
            elem: 'laypage',
            count: 100,
            layout: ['prev', 'page', 'next', 'limit', 'skip'],
            groups: 3,
            jump: function(obj){
            }
        });
    }
    
});