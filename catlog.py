from flask import Flask,redirect,url_for,request,render_template, jsonify
from flask_restful import reqparse
from flask_mysqldb import MySQL
import yaml


app = Flask(__name__)

#Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/query', methods=['POST'])
def query():
	data = request.get_json()
	cur = mysql.connection.cursor()
	if data['query'] == 'SORT':
		if data['props']==0:
			x = "name"
		if data['props']==1:
			x = "name"
		if data['props']==2:
			x = "name desc"

		result = cur.execute("select * from products order by {}".format(x))

		prods = []
		prodDetails = cur.fetchall()
				
		for item in prodDetails:
			prods.append({
				'productID' : item[0],
				'name' : item[1],
				'url' : item[3],
				'price' : item[6]
			})
			
		mysql.connection.commit()
		cur.close()
		return jsonify({'prods':prods})

	if data['query'] == 'FILTER':
		queryStr=""
		if data['brand']:
			s = "("
			for x in range(data['brand']):
				x_val = data['brand'][x];
				s = s+"'"+x_val+"',"  
			s = s[:-1]+")"
			queryStr= queryStr + "brand in " + s

		if data['price']:
			for x in data['price']:
				if x==0:
					queryStr = queryStr + "and price between 0 and 499"
				if x==1:
					queryStr = queryStr + "and price between 500 and 999"
				if x==2:
					queryStr = queryStr + "and price >= 1000"
			
		if data['color']:
			s = "("
			for x in range(data['color']):
				x_val = data['color'][x];
				s = s+"'"+x_val+"',"  
			s = s[:-1]+")"
			queryStr= queryStr + "color in " + s
			
		cur.execute("select * from products where brand in {} and color in {} and price between".format())


# @app.route('/fliter',methods=['POST'])
# def filter():
# 	data = request.get_json()


# @app.route('/validateInventory/<prodID>')
# def val(prodID):
# 	return #"yes" or "no"

# @app.route('/prodDescription/<prodID>')
# def prodDescription(prodID):
# 	return #description

# @app.route('/inventoryUpdate',methods=['POST'])
# def inventoryUpdate():
# 	data = request.get_json()
# 	return #Success or Failure


#Admin CRUD APIs

@app.route('/admin/<type>',methods=['POST', 'DELETE'])
def crudOps(type):
	cur = mysql.connection.cursor()
	if request.method == 'POST':
		if type == 'READ':
			data = request.get_json()

			result = cur.execute("select * from products where {} = '{}'".format(data['category'], data['value']))

			prods = []
			
			if(result > 0):
				prodDetails = cur.fetchall()
				
				for item in prodDetails:
					prods.append({
						'productID' : item[0],
						'name' : item[1],
						'url' : item[3],
						'price' : item[6]
					})
				
			mysql.connection.commit()
			cur.close()
			return jsonify({'prods':prods})

		if type == 'UPDATE':
			data = request.get_json()

			if(data['name']):
				cur.execute("update products set name = '{}' where productID = {}".format(data['name'], data['productID']))

			if(data['url']):
				cur.execute("update products set imageURL = '{}' where productID = {}".format(data['url'], data['productID']))

			if(data['price']):
				cur.execute("update products set price = {} where productID = {}".format(data['price'], data['productID']))

			mysql.connection.commit()
			cur.close()

			return 'success'
		
		# Create product
		data = request.get_json()

		tag = data['brand'] + '-' + data['color'] + '-' + str(data['price'])
			

		cur.execute("insert into products(name, description, imageURL, brand, color, price, category,createTime) values('{}','{}','{}','{}','{}',{},'{}',CURRENT_TIMESTAMP())".format(data['name'],data['description'],data['url'],data['brand'],data['color'],data['price'],data['category']))
		mysql.connection.commit()

		result = cur.execute("select * from products")
		out = cur.fetchall();
		x = out[-1][0];

		cur.execute("insert into tags values({},'{}')".format(x,tag))
		cur.execute("insert into inventory values({},{})".format(x,data['qty']))

		mysql.connection.commit()
		cur.close()

		return 'success'

	#DELETE
	data = request.get_json()
	cur.execute("delete from products where productID = {}".format(data['productID']))
	mysql.connection.commit()
	cur.close()

	return 'success'


if __name__ == '__main__':
	app.debug = True
	app.run()