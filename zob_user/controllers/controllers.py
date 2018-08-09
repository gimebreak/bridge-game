# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
_logger = logging.getLogger(__name__)
import os

from odoo import http
from odoo.http import request
from odoo.service import security
from odoo.service import model

from odoo import SUPERUSER_ID, registry, api

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class GameBrg(http.Controller):
    @http.route('/json/test1',type='json', auth='none',cors='*',csrf=False)
    def test1(self,**kw):
        return "hello!"


    @http.route('/json/api',type='json', auth='user', cors='*', csrf=False )
    def json_api(self, model, method,args, kw):
        return api.call_kw(request.env[model],method,args,kw)
    # @http.route('/json/api',type='json', auth='none', cors='*', csrf=False )
    # def json_api(self,**kw):
    #     json = http.request.jsonrequest
    #     session = self.check_session(json['sid'])
    #     if not session:
    #         return {'message：':'AccessDenied'}

    #     db = session.db
    #     uid = session.uid
    #     user = http.request.env['res.users'].sudo().browse(uid)

    #     model_name = json['model']
    #     method=json['method']
    #     args = json.get('args',() )
    #     kw = json.get('kw',{})
    #     ret = model.execute_kw(db,uid, model_name, method, args, kw)
    #     return ret

    @http.route('/json/uploadimage',type='http', auth='public',cors='*',csrf=False)
    def uploadimage(self,**kw):
        image= http.request.httprequest.data
        with open(BASE_DIR+'/123.jpg','wb+') as f :
            f.write(image)
            f.close()
        return BASE_DIR+'123.jpg'



    @http.route('/json/user/register',type='json', auth='none', cors='*', csrf=False )
    def register(self,**kw):
        json = http.request.jsonrequest
        json=json['params']
        db = json['db']
        user = json['login']
        password = json['password']
        #uid = SUPERUSER_ID
        with registry(db).cursor() as cr:
            # 文件管理
            env = api.Environment(cr, SUPERUSER_ID, {})
            return env['res.users'].register(user,password).id
        
    @http.route('/json/user/reset/password',type='json', auth='none', cors='*', csrf=False )
    def reset_password(self,**kw):
        json = http.request.jsonrequest
        json=json['params']
        db = json['server']
        user = json['user']
        password = json['password']
        #uid = SUPERUSER_ID
        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            return env['res.users'].reset_password(user,password)


    @http.route('/json/user/login',type='json', auth='none', cors='*', csrf=False )
    def login1(self,**kw):
        json = http.request.jsonrequest
        json=json['params']
        #if not request.uid:
        #if request.uid and json.get('sid'):
        #    session = http.root.session_store.get(json['sid'])
        #    return { 'sid': session.sid }

        db = json['db']
        user = json['login']
        password = json['password']
        uid = http.request.env['res.users'].authenticate(
                     db,user,password,None )
        if not uid:return False

        session = http.request.session
        session.db = db
        session.uid = uid
        session.login = user
        session.session_token = uid and security.compute_session_token(session,http.request.env)
        session.context = http.request.env['res.users'].context_get() or {}
        session.context['uid'] = uid
        session._fix_lang(session.context)
        http.root.session_store.save(session)
        return { 'sid': session.sid }  # user info


    def check_session(self,sid):
        try:
            session = http.root.session_store.get(sid)
            if(security.check_session(session,http.request.env)):
                return session
        except:
            return False







