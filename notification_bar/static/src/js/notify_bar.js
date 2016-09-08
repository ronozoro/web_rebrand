/**
 * Created by mostafa.
 */

odoo.define('notification_bar.notify_bar', function (require) {

    var Model = require('web.Model');
    var core = require('web.core');
    var UserMenu = require('web.UserMenu');
    var webclient = require('web.web_client');
    var Widget = require('web.Widget');
    var NotificationBar = Widget.extend({
        template: 'NotificationBar',
        init: function (parent) {
            this._super(parent);
            this.data = parent.data;
            this.nums = parent.nums

        },
        start: function () {
            var self = this;
            this.$("#noti_Button").text(this.nums);
            this.$(".this_is_button").click(function () {
                console.log(this.id);
                window.open(this.id, "_self")
            });
            var mouse_is_inside = false;
            this.$('#notifications').hover(function () {
                mouse_is_inside = true;
            }, function () {
                mouse_is_inside = false;
            });

            $("body").mouseup(function () {
                if (!mouse_is_inside) self.$('#notifications').hide();
            });
            if (self.$('#notifications').is(':hidden')) {
                self.$('#noti_Button').css('background-color', '#2E467C');
            }
            this.$("#noti_Button").click(function () {
                self.$('#notifications').fadeToggle('fast', 'linear', function () {
                    if (self.$('#notifications').is(':hidden')) {
                        self.$('#noti_Button').css('background-color', '#2E467C');
                    }
                    else self.$('#noti_Button').css('background-color', '#FFF');
                });

                return false;
            });

            this.$('#notifications').click(function () {
                return false;
            });
        },

    });
    UserMenu.include({
        do_update: function () {
            this._super();
            var self = this;
            this.data = [];
            this.update_promise.done(function () {
                if (!_.isUndefined(self.notificationBar)) {
                    return;
                }
                var notify_obj = new Model('notification.bar');
                notify_obj.call('get_notifications', ['']).done(function (result) {
                    self.data = result[0];
                    self.nums = result[1];
                    self.notificationBar = new NotificationBar(self);
                    self.notificationBar.prependTo(webclient.$('.oe_systray'));
                });

            });

        },
    });
});