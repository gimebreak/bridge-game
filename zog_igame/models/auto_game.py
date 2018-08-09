from odoo import api, fields, models
import json
import logging
_logger = logging.getLogger(__name__)

class IntelligentGame(models.Model):
    _inherit = 'og.igame'


    # deal_order = '23456789TJQKA'
    # deal_count = 'JQKA'

    @api.model
    def rot_initboard(self):
        max_point = 0
        vals={}
        tmp_deal = self.env['og.deal']
        tmp_board = self.env['og.board']      
        for _ in range(8):
            deal = self.env['og.deal'].create(vals)  
            while deal.ad_pos!='S':
                deal.unlink()
                deal = self.env['og.deal'].create(vals)
            tmp_deal += deal
        table_vals = {'deal_ids':tmp_deal}
        table = self.env['og.table'].create(table_vals)
        for rec in tmp_deal:
            board_vals = {'table_id':table.id,'deal_id':rec.id}
            tmp_board += self.env['og.board'].create(board_vals)
        deal_ids = tmp_deal.mapped('id')
        board_ids=tmp_board.mapped('id')
        return board_ids,deal_ids
        # return True   

    def player_bid(self,pos,name,board_id):
        vals = {'pos','name'}
        self.env['og.board.call']
