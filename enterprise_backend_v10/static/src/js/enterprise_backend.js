odoo.define('enterprise_backend', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var pyeval = require('web.pyeval');
    var Menu = require('web.Menu');
    var Model = require('web.DataModel');
    var PlannerLauncher = require('web.planner').PlannerLauncher;
    var WebClient = require('web.WebClient');
    var SearchView = require('web.SearchView');
    var ActionManager = require('web.ActionManager');
    var Widget = require('web.Widget');
    var ViewManager = require('web.ViewManager');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');
    var Dialog = require('web.Dialog');
    var ControlPanel = require('web.ControlPanel');
    var data = require('web.data');
    var data_manager = require('web.data_manager');
    var Bus = require('web.Bus');

    var Action = core.Class.extend({
        init: function (action) {
            this.action_descr = action;
            this.title = action.display_name || action.name;
        },
        restore: function () {
            if (this.on_reverse_breadcrumb_callback) {
                return this.on_reverse_breadcrumb_callback();
            }
        },

        detach: function () {
        },

        destroy: function () {
        },

        set_on_reverse_breadcrumb: function (callback) {
            this.on_reverse_breadcrumb_callback = callback;
        },

        set_scrollTop: function () {
        },

        set_fragment: function ($fragment) {
            this.$fragment = $fragment;
        },

        get_scrollTop: function () {
            return 0;
        },

        get_action_descr: function () {
            return this.action_descr;
        },

        get_breadcrumbs: function () {
            return {title: this.title, action: this};
        },

        get_nb_views: function () {
            return 0;
        },

        get_fragment: function () {
            return this.$fragment;
        },

        get_active_view: function () {
            return '';
        },
    });

    var WidgetActionxs = Action.extend({

        init: function (action, widget) {
            this._super(action);

            this.widget = widget;
            if (!this.widget.get('title')) {
                this.widget.set('title', this.title);
            }
            this.widget.on('change:title', this, function (widget) {
                this.title = widget.get('title');
            });
        },

        restore: function () {
            var self = this;
            return $.when(this._super()).then(function () {
                return self.widget.do_show();
            });
        },

        detach: function () {
            // Hack to remove badly inserted nvd3 tooltips ; should be removed when upgrading nvd3 lib
            $('body > .nvtooltip').remove();

            return framework.detach([{widget: this.widget}]);
        },

        destroy: function () {
            this.widget.destroy();
        },
    });

    var ViewManagerActionxs = WidgetActionxs.extend({
        restore: function (view_index) {
            var _super = this._super.bind(this);
            return this.widget.select_view(view_index).then(function () {
                return _super();
            });
        },
        set_on_reverse_breadcrumb: function (callback, scrollTop) {
            this._super(callback);
            this.set_scrollTop(scrollTop);
        },

        set_scrollTop: function (scrollTop) {
        },

        get_scrollTop: function () {
            return this.widget.active_view.controller.get_scrollTop();
        },

        get_breadcrumbs: function () {
            var self = this;
            return this.widget.view_stack.map(function (view, index) {
                return {
                    title: view.controller.get('title') || self.title,
                    index: index,
                    action: self,
                };
            });
        },

        get_nb_views: function () {
            return this.widget.view_stack.length;
        },

        get_active_view: function () {
            return this.widget.active_view.type;
        }
    });

    ActionManager.include({
        push_action: function (widget, action_descr, options) {
            var self = this;
            var old_action_stack = this.action_stack;
            var old_action = this.inner_action;
            var old_widget = this.inner_widget;
            var actions_to_destroy;
            options = options || {};

            // Empty action_stack or replace last action if requested
            if (options.clear_breadcrumbs) {
                actions_to_destroy = this.action_stack;
                this.action_stack = [];
            } else if (options.replace_last_action && this.action_stack.length > 0) {
                actions_to_destroy = [this.action_stack.pop()];
            }

            // Instantiate the new action
            var new_action;
            if (widget instanceof ViewManager) {
                new_action = new ViewManagerActionxs(action_descr, widget);
            } else if (widget instanceof Widget) {
                new_action = new WidgetActionxs(action_descr, widget);
            } else {
                new_action = new Action(action_descr);
            }

            // Set on_reverse_breadcrumb callback on previous inner_action
            if (this.webclient && old_action) {
                old_action.set_on_reverse_breadcrumb(options.on_reverse_breadcrumb, this.webclient.get_scrollTop());
            }

            // Update action_stack (must be done before appendTo to properly
            // compute the breadcrumbs and to perform do_push_state)
            this.action_stack.push(new_action);
            this.inner_action = new_action;
            this.inner_widget = widget;

            if (widget.need_control_panel) {
                // Set the ControlPanel bus on the widget to allow it to communicate its status
                widget.set_cp_bus(this.main_control_panel.get_bus());
            }

            // render the inner_widget in a fragment, and append it to the
            // document only when it's ready
            var new_widget_fragment = document.createDocumentFragment();
            return $.when(this.inner_widget.appendTo(new_widget_fragment)).done(function () {
                // Detach the fragment of the previous action and store it within the action
                if (old_action) {
                    old_action.set_fragment(old_action.detach());
                }
                if (!widget.need_control_panel) {
                    // Hide the main ControlPanel for widgets that do not use it
                    self.main_control_panel.do_hide();
                }
                framework.append(self.$el, new_widget_fragment, {
                    in_DOM: self.is_in_DOM,
                    callbacks: [{widget: self.inner_widget}],
                });
                if (actions_to_destroy) {
                    self.clear_action_stack(actions_to_destroy);
                }
                self.toggle_fullscreen();
                self.trigger_up('current_action_updated', {action: new_action});
            }).fail(function () {
                // Destroy failed action and restore internal state
                new_action.destroy();
                self.action_stack = old_action_stack;
                self.inner_action = old_action;
                self.inner_widget = old_widget;
            });
        },
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

