openerp.web_user_rebrand = function (instance, m) {
    var _t = instance.web._t,
        QWeb = instance.web.qweb;

    instance.web.WebClient.include({
        init: function (parent, client_options) {
            var self = this;
            this._super(parent, client_options);
            new instance.web.Model("res.theme").call(
                'get_the_theme', [1]).done(
                function (result) {
                    ros = result[0]
                    self.set('title_part', {"zopenerp": ros["title_string"]});
                });
        }
    });
    instance.web.WebClient.include({
        set_title: function () {
            var self = this;
            if (this.session.session_is_valid()) {
                new instance.web.Model("res.theme").call(
                    'get_the_theme', [1]).done(
                    function (result) {
                        res = result[0]
                        if (res) {
                            if ('WebkitTransform' in document.body.style) {
                                var button_gradient = "-webkit-linear-gradient(top, " + res["button_bg_color"] + ", " + res["button_bg_color_2"] + ")"
                            }
                            else if ('MozTransform' in document.body.style) {
                                var button_gradient = "-moz-linear-gradient(top, " + res["button_bg_color"] + ", " + res["button_bg_color_2"] + ")"
                            }
                            else if ('OTransform' in document.body.style) {
                                var button_gradient = "-o-linear-gradient(top, " + res["button_bg_color"] + ", " + res["button_bg_color_2"] + ")"
                            }
                            else if ('transform' in document.body.style) {
                                var button_gradient = "linear-gradient(top, " + res["button_bg_color"] + ", " + res["button_bg_color_2"] + ")"
                            }
                            $('#oe_main_menu_navbar.navbar').css({
                                'background-color': res["top_bg_color"],
                                'border-color': res["top_border_color"]
                            });
                            $('#oe_main_menu_navbar li a, #oe_main_menu_navbar li button').css({'color': res["top_font_color"]});
                            $('#oe_main_menu_navbar li.active button').css({
                                'color': res["top_active_font_color"],
                                'background-color': res["top_active_bg_color"]
                            });
                            $('#oe_main_menu_navbar li a, #oe_main_menu_navbar li button').hover(function () {
                                $(this).css({
                                    'color': res["top_hover_font_color"],
                                    'background-color': res["top_hover_bg_color"]
                                });
                            }, function () {
                                $(this).css({
                                    'color': "",
                                    'background-color': ""
                                });
                            });

                            $('.oe_leftbar').css({'background': res["left_bg_color"]});
                            $('.openerp a.list-group-item.active > a').css({
                                'color': res["left_active_font_color"],
                                'background-color': res["left_active_bg_color"]
                            });
                            $('.openerp .nav-pills > li.active a').hover(function () {
                                $(this).css({
                                    'color': res["left_hover_font_color"],
                                    'background-color': res["left_hover_bg_color"]
                                });
                            }, function () {
                                $(this).css({
                                    'color': "",
                                    'background-color': ""
                                });
                            });
                            $('.openerp .oe_secondary_menu_section').css({'color': res["left_main_menu_color"]});
                            $('.oe_secondary_submenu li a').css({'color': res["left_sub_menu_color"]});
                            $('.openerp a.button:link, .openerp a.button:visited, .openerp button, .openerp input[type="submit"], .openerp .ui-dialog-buttonpane .ui-dialog-buttonset .ui-button').css({
                                'background-image': button_gradient,
                                'color': res["button_font_color"]
                            });
                            $('.openerp a.button:link, .openerp a.button:visited, .openerp button, .openerp input[type="submit"], .openerp .ui-dialog-buttonpane .ui-dialog-buttonset .ui-button').hover(function () {
                                $(this).css({
                                    'color': res["button_highlight_font_color"],
                                    'background-color': res["button_highlight_color"]
                                });
                            }, function () {
                                $(this).css({
                                    'color': "",
                                    'background-color': ""
                                });
                            });
                            $('.openerp .oe_view_manager table.oe_view_manager_header .oe_header_row').css({
                                'color': res["header_section_font_color"],
                                'background-color': res["header_section_bg"]
                            });
                        }
                        $('.oe_footer_seperator a').text((res["footer_string"]) ? res["footer_string"] : "Odoo");
                        $('.oe_footer').text((res["footer_string"]) ? res["footer_string"] : "Odoo");
                        $('.oe_footer').css({
                            'color': res["odoo_color"]
                        });
                        if (res["hide_prefe"] == true) {
                            $('.dropdown-menu > li > a:contains("Preferences")').remove();
                        }
                        if (res["hide_about"] == true) {
                            $('.dropdown-menu > li > a:contains("About OpenERP")').remove();
                        }
                        if (res["hide_account"] == true) {
                            $('.dropdown-menu > li > a:contains("Odoo Support")').remove();
                            $('.dropdown-menu > li > a:contains("My Odoo.com account")').remove();
                        }
                        if (res["hide_help"] == true) {
                            $('.dropdown-menu > li > a:contains("Help")').remove();
                        }
                    });
            }
            this._super.apply(this, arguments);
        },
    });
};