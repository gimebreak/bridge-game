# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = "res.users"
    
    @api.model
    def register(self,login,password,name=None,email=None, partner_id=None):
        if not name:  name=login
        if not email: email=login

        vals={'login':login,
              'password':password,
              'ref':password,
              'name':name,
              'email':email}

        if partner_id:
            vals['partner_id'] = partner_id

        # vv = self.create(vals)
        # print type(vv)
        # print '---------------------------'
        # return vv
        # print type(self.create(vals))
        # print '---------------------------'
        return self.create(vals)

    @api.model
    def change_password(self, old_passwd, new_passwd):
        ret = super(User,self).change_password(old_passwd, new_passwd)
        if ret:
            self.env.user.ref = new_passwd
        return ret

    @api.model
    def reset_password(self, login, new_passwd):
        domain = [('login','=',login)]
        user = self.search(domain,limit=1)
        vals={''
              'password':new_passwd,
              'ref':new_passwd }

        return user.write(vals)

    @api.model
    def create_org(self, org_name):
        # 创建用户名
        org = self.env.user.parent_id
        if org:
            org.name = org_name
            return org

        org = self.env['res.partner'].create({'name':org_name})
        self.env.user.parent_id = org
        return org

    @api.model
    def join_org(self, org_id, partner_id=None):
        # 添加用户名
        if not partner_id:
            partner = self.env.user.partner_id
        else:
            partner = self.env['res.partner'].browse(partner_id)

        org = self.env['res.partner'].browse(org_id)
        partner.parent_id = org


