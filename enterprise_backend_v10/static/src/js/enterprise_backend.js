odoo.define('enterprise_backend', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var Menu = require('web.Menu');
    var Model = require('web.DataModel');
    var PlannerLauncher = require('web.planner').PlannerLauncher;
    var WebClient = require('web.WebClient');
    var SearchView = require('web.SearchView');
    $(document).ready(function () {
        $(".o_mail_chat").css({"position": "", "top": "0", "bottom": "0", "right": "0", "height": "100%"});
        $(".o_mail_thread").css({
            "-webkit-box-flex:": "1",
            "-webkit-flex": "1 0 0",
            "flex": "1 0 0",
            "padding": "0 0 15px 0",
            "overflow": ""
        });
    });

    PlannerLauncher.include({
        on_menu_clicked: function (menu_id) {
            if (menu_id !== undefined) {
                if (_.contains(_.keys(this.planner_apps), menu_id.toString())) {
                    this.setup(this.planner_apps[menu_id]);
                    this.need_reflow = true;
                }
            }
            else {
                this.$el.hide();
                this.need_reflow = true;
            }
            if (this.need_reflow) {
                core.bus.trigger('resize');
                this.need_reflow = false;
            }

            if (this.dialog) {
                this.dialog.$el.modal('hide');
                this.dialog.$el.detach();
            }
        },
    });
    SearchView.include({
        toggle_visibility: function (is_visible) {
            this.do_toggle(!this.headless && is_visible);
            if (this.$buttons) {
                this.$buttons.toggle(!this.headless && is_visible && this.visible_filters);
            }
            if (!this.headless && is_visible && !jQuery.browser.mobile) {
                this.$('div.oe_searchview_input').last().focus();
            }
        },
    });

    WebClient.include({
        bind_hashchange: function () {
            var self = this;
            $(window).bind('hashchange', this.on_hashchange);
            var state = $.bbq.getState(true);
            if (_.isEmpty(state) || state.action == "login") {
                self.menu.is_bound.done(function () {
                    new Model("res.users").call("read", [session.uid, ["action_id"]]).done(function (data) {
                        if (data.action_id) {
                            self.action_manager.do_action(data.action_id[0]);
                            self.menu.open_action(data.action_id[0]);
                        } else {
                            self.$el.find('#appsbar_toggle').toggleClass('fa-chevron-left');
                            self.$el.find('.oe_appsbar').toggleClass('hide');
                            self.$el.find(".navbar-collapse.collapse.in").removeClass("in");
                        }
                    });
                });
            } else {
                $(window).trigger('hashchange');
            }
        },
    });

    Menu.include({
        bind_menu: function () {
            var self = this;
            $(".oe_menu_leaf").click(function (event) {
                var addressValue = $(this).attr("href");
                window.location.replace(window.location.origin + addressValue)
            });
            $(".oe_app a").click(function (event) {
                var appname = $(this).find('.oe_app_caption').html();
                $('.app-title').text(appname);
                $("#oe_main_menu_placeholder").removeClass("in");
                var addressValue = $(this).attr("href");
                window.location.replace(window.location.origin + addressValue)
            });
            var body = self.$el.parents('body');
            if ($('nav ul li.tnav ul').closest("li").children("ul").length) {
                $('nav ul li.tnav ul').closest("li").children("ul li a").append('<b class="caret"></b>');
            }
            $('nav#oe_main_menu_navbar ul li ul.oe_secondary_submenu').addClass("tnav");
            body.on('click', '#appsbar_toggle', function (event) {
                event.preventDefault();
                $(this).toggleClass('fa-chevron-left');
                body.find('.oe_appsbar').toggleClass('hide');
                $(".navbar-collapse.collapse.in").removeClass("in");
            });
            $(".o_planner_systray").show();
            $(".navbar-toggle").click(function () {
                $("#right_menu_bar").addClass("hide");
                $("#right_menu_bar").addClass("collapse in");
                $("#oe_main_menu_placeholder").removeClass("hide");
                $(".fa.fa-th.fa-chevron-left").removeClass("fa-chevron-left");
            });
            $("a[data-action-model]").click(function () {
                $(".navbar-collapse.collapse.in").removeClass("in");
            });
            this.$secondary_menus = this.$el.parents().find('.oe_secondary_menus_container');

            this.$secondary_menus.on('click', 'a[data-menu]', this.on_menu_click);
            this.$el.on('click', 'a[data-menu]', function (event) {
                event.preventDefault();
                var menu_id = $(event.currentTarget).data('menu');
                var needaction = $(event.target).is('div#menu_counter');
                core.bus.trigger('change_menu_section', menu_id, needaction);
            });
            this.trigger('menu_bound');
            this.is_bound.resolve();

        },
        open_menu: function (id) {
            var self = this;
            this.current_menu = id;
            session.active_id = id;
            var $clicked_menu
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);
            $('.oe_appsbar').addClass('hide');
            $('#appsbar_toggle').removeClass('fa-chevron-left');
            $('.oe_application_menu_placeholder > ul').addClass('hide');
            var clicked_menu_top = $('.oe_application_menu_placeholder a[data-menu=' + id + ']');
            if (clicked_menu_top.length > 0) {
                clicked_menu_top.parents(".hide").removeClass('hide');
            } else {
                $('.oe_application_menu_placeholder > ul[data-menu-parent=' + id + ']').removeClass('hide');
            }
            setTimeout(function () {
                var height = $('#announcement_bar_table').outerHeight()
                    + $('#oe_main_menu_navbar').outerHeight();
                $('.openerp_webclient_container').css('height', 'calc(100% - ' + height + 'px)');
            }, 500);
        }, menu_click: function (id, needaction) {

            if (!id) {
                return;
            }
            var $item = this.$el.find('a[data-menu=' + id + ']');
            if (!$item.length) {
                $item = this.$secondary_menus.find('a[data-menu=' + id + ']');
            }
            var action_id = $item.data('action-id');
            if (!action_id) {
                if (this.$el.has($item).length) {
                    var $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + id + ']');
                    var $items = $sub_menu.find('a[data-action-id]').filter('[data-action-id!=""]');
                    if ($items.length) {
                        action_id = $items.data('action-id');
                        id = $items.data('menu');
                    }
                }
            }
            if (action_id) {
                this.trigger('menu_click', {
                    action_id: action_id,
                    needaction: needaction,
                    id: id,
                    previous_menu_id: this.current_menu
                }, $item);
            } else {
            }
            this.open_menu(id);
        },
    });
});
;
