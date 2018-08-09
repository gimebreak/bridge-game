# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import random

class IntelligentGameApi(models.Model):
    _inherit = "og.igame"

    @api.model
    @api.returns('self')
    def create_bridge_team(self,name,org_type=None, score_uom=None):
        vals = {'name':name, 'game_type':'bridge', 'match_type':'team'}
        if org_type: vals['org_type'] = org_type
        if score_uom: vals['score_uom'] = score_uom
        gid = self.create(vals)
        return gid

    @api.model
    @api.returns('self')
    def create_child(self,name,parent_id,org_type=None,sequence=None):
        vals = {'name':name, 'parent_id': parent_id}
        parent = self.env['og.igame'].browse(parent_id)
        vals['game_type'] = parent.game_type
        vals['match_type'] = parent.match_type
        if org_type: vals['org_type'] = org_type
        if sequence: vals['sequence'] = sequence
        vals['score_uom'] = parent.score_uom
        return self.create(vals)


    @api.model
    @api.returns('self')
    def search_bridge_team(self,domain):
        self = self.sudo()
        dm = [('parent_id','=',None),('game_type','=','bridge'),
              ('match_type','=','team')  ] + domain
        gms = self.env['og.igame'].search(dm)
        return gms  #self.env['og.igame'].browse(gid)
        #return [{'name':gm.name, 'id':gm.id}  for gm in gms ]

    @api.model
    def search2(self,domain):
        gms = self.search_bridge_team(domain=domain)
        return [{'name': gm.name, 'id': gm.id} for gm in gms]

    @api.model
    @api.returns('self')
    def register1(self,game_id):
        me = self.env.user
        partner_id = me.parent_id.id
        self = self.sudo()
        game = self.env['og.igame'].browse(game_id)
        sc = self.env['og.igame.score'].search([('igame_id','=',game_id),
                                    ('partner_id','=',partner_id)])
        if not sc:
            ret = self.env['og.igame.score'].create(
                    {'igame_id':game_id,'partner_id':partner_id }) 

        return game

    @api.multi
    @api.returns('self')
    def register(self):
        me = self.env.user
        partner_id = me.parent_id.id
        self = self.sudo()
        sc = self.score_ids.filtered(
             lambda sc1: sc1.partner_id.id == partner_id)
        if not sc:
            sc = self.env['og.igame.score'].create(
                    {'igame_id':self.id,'partner_id':partner_id }) 

        return sc

    @api.model
    @api.returns('self')
    def cancel(self,game_id):
        me = self.env.user
        partner_id = me.parent_id.id
        self = self.sudo()
        game = self.env['og.igame'].browse(game_id)
        #sc = self.env['og.igame.score'].search([('igame_id','=',game_id),
        #                            ('partner_id','=',partner_id)])

        sc = game.score_ids.filtered(lambda s: s.partner_id.id == partner_id)
        if sc:
            sc.unlink()

        return game

    @api.multi
    def register_player(self, player_id,team_id=None):
        for rec in self:
            rec._register_player(player_id,team_id)

    def _register_player(self, player_id, team_id=None):
        if not team_id:
            team_id = self.env.user.parent_id.id
        sc = self.score_ids.filtered(lambda sc: sc.partner_id == team_id)
        player = self.env['res.partner'].browse(player_id)
        sc.player_ids |= player

    @api.multi   # 创建,没有比赛id
    def get_group_partner(self,partner_id):  # 队伍id
        gs = self.group_ids.filtered( lambda g: partner_id in g.partner_ids )
        g = gs and gs[0] or self.env['og.igame.group']
        return g.name


    @api.multi   # 创建,没有比赛id
    def set_group_partner(self,group_name,number,partner_id):  # 队伍id
        gid = self.id
        #gs = self.group_ids.filtered(lambda g: g.name == group_name)

        gs = self.env['og.igame.group'].search(
              [('name','=',group_name),('igame_id','=',gid)  ] )

        g = gs and gs[0] or None
        if not g:
            vals = {'igame_id':gid,'name':group_name}
            g = self.env['og.igame.group'].create(vals)

        ptn = self.env['res.partner'].browse(partner_id)
        g.partner_ids += ptn
        return True
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
#search users,return all the users's information stored in the res.partner

    @api.model
    def get_users(self):
        dm=[]
        a=[]
        users=self.env['res.users'].search(dm)
        for rec in users:
            if not rec.partner_id.name == 'Administrator':
                a.append({'id':rec.partner_id.id,'name':rec.partner_id.name})
        return a

    @api.model
    # @api.returns('self')
    def register_game(self,game_id,team_id,kwargs):
        self=self.sudo()
        iteam=self.env['og.igame.team'].search([('partner_id','=',team_id),('igame_id','=',None)])
        vals={'igame_id':game_id,'partner_id':iteam.partner_id.id}
        new_team=self.env['og.igame.team'].create(vals)
        for rec in kwargs:
            player_id=rec['id']
            role=rec['role']
            vals={'partner_id':player_id,'role':role,'team_id':new_team.id}
            self.env['og.igame.team.player'].create(vals)
        return True


    # @api.multi
    # def auto_groups(self):
    #     igame_id = self.id
    #     teams = self.team_ids
    #     teams_id = teams.mapped('id')
    #     letter= 65
    #     if len(teams)%4 != 0:
    #         return 'could not be grouped'
    #     random.shuffle(teams_id)
    #     group_list = []

    #     for i in range(0,len(teams_id),4):
    #         b = teams_id[i:i+4]
    #         group_list.append(b)

    #     for group in group_list:
    #         vals = {'igame_id':igame_id,'name':chr(letter)}
    #         letter += 1
    #         rec = self.env['og.igame.group'].create(vals)
    #         rec.team_ids = group
    #         # return group[0]
    #     return True


    # @api.multi
    # def auto_rounds(self):
    #     groups = self.group_ids
    #     group = groups and groups[0] or None
    #     team_num = len(group.team_ids)
    #     round_ids = []
    #     for r in range(1,team_num):
    #         deals_id = self._round_random_deals()
    #         vals = {'igame_id':self.id,'number':r}
    #         round_id = self.env['og.igame.round'].create(vals)
    #         round_id.deal_ids = deals_id
    #         # round_ids.append(round_id.id)
    #     return True
    #     # self._round_random_deals(round_ids)

    # def _round_random_deals(self):

    #     deals = []
    #     deal_set = []
    #     tmp = self.env['og.deal']
    #     # deals = self.env['og.deal'].search([]).mapped('number')
    #     deals = self.env['og.deal'].search([])
    #     deals_number = deals.mapped('number')
    #     deals_id = deals.mapped('id')
    #     carded = []
    #     if len(deals_number) < 8 : 
    #         return False        
    #     # for r in range(len(round_ids)):
    #     s = random.randint(0,len(deals_id)-1)
    #     for i in (1,2,3,4,5,6,7,0):
    #         while deals_number[s] % 8 != i or s in carded:
    #             s = random.randint(1,len(deals_id)-1)
    #         carded.append(s)
    #         tmp += self.env['og.deal'].search([('id','=',deals_id[s])])
    #     # round_deals = self.env['og.round'].browse(round_ids[r]).deal_ids
    #     round_deals = tmp.mapped('id')      
    #     return round_deals

    # @api.model
    # def islogin(self,user_id):
    #     status =self.env['res.users'].browse(user_id).im_status



#--------------------2018.6.26----------------
class IntelligentGameTeam(models.Model):
    _inherit="og.igame.team"

# $$$$$
# create a team,where team info are added into 'res.partner' and 'og.igame team'
# the parent_id field of a team in 'res.partner' points to user that creates the team
# and the og.igame.team's partner_id points to the id of a team in 'res.partner'
# and no game_id is added to the og.igame.team in this function which indicates that the team created here
# only represents a team,where you can add players 
# 
    @api.model
    # @api.returns('self')
    # def create_team(self,team_name,kwargs):   
    def create_team(self,team_name,kwargs):               
        user_id=self.env.user.id
        user=self.env['res.users'].search([('id','=',user_id)])
        partner=user.partner_id
#user's partner info
        self=self.sudo()
        team_id=self.env['res.partner'].search([('name','=',team_name)])
        if team_id:return False
        vals={'name':team_name}
        t=self.env['res.partner'].create(vals)
#create team in res.parner
        # team=self.env['res.partner'].search([('name','=',team_name)])
        info={'parent_id':partner.id,'partner_id':t.id}
        tid=self.create(info)
        # s=tid.id
#link a team in res.partner to og.igame.team which means a team you can add players
        for player in kwargs:
            vals={'partner_id':player,'team_id':tid.id}
            self.env['og.igame.team.player'].create(vals)
#add player to the team
#default role : "player"
        return t.id
#$$$$$
#get players that belong to a team
#trigger the team and returns a list of players
    @api.model
    def get_teamplayer(self,team_id): 
        self=self.sudo()
        team=self.browse(team_id)
        players=team.player_ids
        player=[{'id':rec.partner_id.id,'name':rec.partner_id.name} for rec in players]
        return player

#get all the teams of a user,returns team.id and team name and player's name !!!!!!!!
    @api.model
    # @api.returns('self')
    def get_teams(self):
        res=[]
        
        user=self.env.user.partner_id #get user'partner
        self=self.sudo()
        player=self.env['og.igame.team.player'].search([('partner_id','=',user.id),('role','=',None)]) #get teams of a player
        # team=self.env['res.partner'].search([('parent_id','=',user.id)])
        # t=player[0].team_id.player_ids
        for rec in player:
            players=rec.team_id.player_ids
            team=rec.team_id.partner_id
        #   players=team.player_ids # find players of a team in og.igame.team.players
            cache=[]
            for attendee in players:
                player_id=attendee.partner_id.id
                player_name=attendee.partner_id.name
                player_info={'id':player_id,'playername':player_name}
                cache.append(player_info)
            info={'id':team.id,'teamname':team.name,'players':cache}
            res.append(info)
        return res



#get all the teams where I am the creator        
    @api.model
    def get_own_teams(self):
        res=[]
        user=self.env.user.partner_id #get user'partner
        self=self.sudo()
        own_team=self.env['res.partner'].search([('parent_id','=',user.id)])

        for rec in own_team:
            team_id=rec.id
            iteam=self.env['og.igame.team'].search([('partner_id','=',team_id),('igame_id','=',None)])
            iplayers=iteam.player_ids
            cache=[]
            for attendee in iplayers:
                player_id=attendee.partner_id.id
                player_name=attendee.partner_id.name
                player_info={'id':player_id,'playername':player_name}
                cache.append(player_info)
            info={'id':team_id,'teamname':rec.name,'players':cache}
            res.append(info)
        return res
      
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

    # @api.model
    # @api.returns('self')
    # def copy_team(self):
    #     self=self.sudo()
    #     team=self.browse(1)
    #     a=self.create(team)
    #     return a


    # @api.model
    # @api.returns('self')
    # def register_team(self,game_name,team_name,kwargs):
    #     self=self.sudo()
    #     team=self.env['res.partner'].search([('name','=',team_name)])
    #     iteam=self.search([('partner_id','=',team.id),('igame_id','=',None)])
    #     game_id=self.env['og.igame'].search([('name','=',game_name),])
    #     # dm=[('partner_id','=',team_id.id),('igame_id','=',game_id.id)]

    #     # check=self.search(dm)
    #     vals={'igame_id':game_id,'team_id':iteam.partner_id.id}
    #     self.create(vals)

    #     for rec in iteam.player_ids:
    #         self.env('og.igame.team.player').create('')
    #     self.create()
    #     return iteam
        # if not check:
        #     info={'partner_id':team_id.id,'igame_id':game_id.id}
        #     tid=self.create(info)
        #     return tid
        # else:
        #     return check
    
    # @api.model
    # @api.returns('self')
    # def remove_team(self,team_name):
    #     self=self.sudo()
    #     team=self.env['res.partner'].search([('name','=',team_name)])
    #     team_id=self.search([('partner_id','=',team.id)])
    #     team_id.unlink()
    #     return team_id








class IntelligentTeamPlayer(models.Model):
    _inherit='og.igame.team.player'

#     @api.model
#     @api.returns('self')
#     def create_player(self,player_name,team_name,game_name,role='player'):
#         self=self.sudo()
#         player_id=self.env['res.partner'].search([('name','=',player_name)])
#         game_id=self.env['og.igame'].search([('name','=',game_name)])
#         team_id=self.env['res.partner'].search([('name','=',team_name)])
#         iteam_id=self.env['og.igame.team'].search([('igame_id','=',game_id.id),
#                                             ('partner_id','=',team_id.id)])
#         info={'team_id':iteam_id.id,'partner_id':player_id.id,'role':role}
#         pid=self.create(info)
#         return pid
# #!!!!original version


#     @api.model
#     @api.returns('self')
#     def create_channel(self,name):
#         self=self.sudo()
#         s=self.env['res.partner'].search([('name','=',name)])
#         return s
#---------------2018.7.30-----------------------
    @api.model
    def get_matches(self):
        partner_id = self.env.user.partner_id.id
        self = self.sudo()
        inteams = self.env['og.igame.team.player'].search([('partner_id','=',partner_id)])
        tables = []
        for me in inteams:
            lines = me.team_id.line_ids
            for line in lines:
                close_table_id = line.match_id.close_table_id
                open_table_id = line.match_id.open_table_id
                close_table = line.match_id.close_table_id.partner_ids.mapped('id')
                open_table = line.match_id.open_table_id.partner_ids.mapped('id')
                if partner_id in close_table:
                    if self.check_matches(line,close_table_id):    
                        tables.append(line.match_id.close_table_id.id)
                    continue
                if partner_id in open_table:
                    if self.check_matches(open_table_id): 
                        tables.append(line.match_id.open_table_id.id)
                    continue
        return tables

    def check_matches(self,table):

        board_undone = []
        for board in table.board_ids:
            if board.result == None:
                board_undone.append(board.id)           
        if board_undone != None:
            return True
        else: return False
 
    @api.model
    @api.returns('self')
    def create_player(self,player_name,team_name,game_name,role='player'):
        self=self.sudo()
        player_id=self.env['res.partner'].search([('name','=',player_name)])
        game_id=self.env['og.igame'].search([('name','=',game_name)])
        team_id=self.env['res.partner'].search([('name','=',team_name)])
        iteam_id=self.env['og.igame.team'].search([('igame_id','=',game_id.id),
                                            ('partner_id','=',team_id.id)])
        info={'team_id':iteam_id.id,'partner_id':player_id.id,'role':role}
        pid=self.create(info)
        return pid



  
# class IntelligentGameGroup(models.Model):
#     _inherit = "og.igame.group"
#
#     @api.model
#     @api.returns('self')
#     def set_group_partner(self, group_name, number, game_id, partner_id):  # 队伍id
#
#         gs = self.search( [('name','=',group_name),('igame_id','=',game_id)  ] )
#
#         g = gs and gs[0] or None
#         if not g:
#             vals = {'igame_id': game_id, 'name': group_name}
#             g = self.create(vals)
#
#         ptn = self.env['res.partner'].browse(partner_id)
#         g.partner_ids += ptn
#
#         return g


# if not partner_id:
        #    partner = self.env.user.partner_id
        # else:
        #    partner = self.env['res.partner'].browse(partner_id)

        #org = self.env['res.partner'].browse(org_id)
        #partner.parent_id = org

        #if not group_name:
         #   return group_name.create(group_name)


""" 

    def get_rooms_team(self):
        domain = [('game_type', '=', 'bridge'),
                  ('match_type','=','team'),
                  ('org_type','in',['swiss','circle']) ]
        #uid = self.env.uid
        gm = self.env['og.igame'].sudo().search(domain )
        rounds = gm.mapped('round_ids')
        return rounds.read(['name','round'])



    @api.model
    def get_games_team(self):
        domain = [('game_type', '=', 'bridge'),
                  ('parent_id','=',None),
                  ('match_type', '=', 'team') ]
        fields = ['name', 'org_type', 'score_uom' ]
        gm = self.env['og.igame'].sudo().search(domain)
        return gm.read(fields)

    @api.model
    def get_games_pair(self):
        domain = [('game_type', '=', 'bridge'),
                  ('parent_id','=',None),
                  ('match_type', '=', 'pair') ]
        fields = ['name', 'org_type', 'score_uom' ]
        gm = self.env['og.igame'].search(domain)
        return gm.read(fields)

    @api.model
    def post_games_team(self, name,**kw):
        #kw:  org_type=None, score_uom=None, score_type=None
        if kw.get('score_uom') and kw.get('score_type'):
            del kw['score_type']
        vals = {'name':name, 'game_type':'bridge', 'match_type':'team'}
        vals.update( kw )
        return self.env['og.igame'].create(vals).id

    @api.model
    def post_games_pair(self, name,**kw):
        #kw:  org_type=None, score_uom=None, score_type=None
        if kw.get('score_uom') and kw.get('score_type'):
            del kw['score_type']
        vals = {'name':name, 'game_type':'bridge', 'match_type':'pair'}
        vals.update( kw )
        return self.env['og.igame'].create(vals).id


"""



