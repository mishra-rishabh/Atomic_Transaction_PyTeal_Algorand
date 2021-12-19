""" 
  reference: https://pyteal.readthedocs.io/en/stable/examples.html
"""

from pyteal import * ;
from decouple import config

senderBro = Addr( config( "SENDER_ADDR" ) )
receiverBro = Addr( config( "RECEIVER_ADDR" ) )
key = config( "SECRET_KEY" )
secret_key = Bytes( "base32" , key )
timeout = 3000

def hashedTimeLC(
   tmpl_seller = senderBro , tmpl_buyer = receiverBro ,
   tmpl_fee = 1000, tmpl_secret = secret_key ,
   tmpl_hash_function = Sha256 , tmpl_timeout = timeout
):
  fee_condition = Txn.fee() < Int( tmpl_fee )

  safety_condition = And(
    Txn.type_enum() == TxnType.Payment ,
    # or
    # Txn.type_enum() == Int( 1 ) ,
    Txn.close_remainder_to() == Global.zero_address() ,
    Txn.rekey_to() == Global.zero_address()
  )

  receiver_condition = And(
    Txn.receiver() == tmpl_seller ,
    tmpl_hash_function( Arg( 0 ) ) == tmpl_secret
  )

  escrow_condition = And(
    Txn.receiver() == tmpl_buyer ,
    Txn.first_valid() > Int( tmpl_timeout )
  )

  return And( fee_condition , safety_condition , Or( receiver_condition , escrow_condition ) )

if __name__ == "__main__":
  with open( "CompiledTealCode/atomic_transaction.teal" , "w" ) as f:
    compiledCode = compileTeal( hashedTimeLC() , Mode.Signature , version = 5 )
    f.write( compiledCode )