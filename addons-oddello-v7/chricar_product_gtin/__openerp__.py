{
	"name" : "Product GTIN EAN8 EAN13 UPC JPC Support",
	"version" : "2.0",
	"author" : "ChriCar Beteiligungs- und Beratungs- GmbH",
	"website" : "http://www.chricar.at/ChriCar",
	"category" : "Generic Modules/Others",
	"depends" : ["product"],
	"description" : """Replaces the EAN13 code completion with a checkroutine for EAN13, EAN8, JPC, UPC and GTIN
    makes EAN visible in simplified view
    YOU MUST comment constraints in product/product.py manually 
    #_constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]
    or apply the patch  provided in
    https://bugs.launchpad.net/openobject-server/+bug/700451
        """,
	"data" : ["chricar_product_gtin_view.xml"],
	
	"installable": True,
	"auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: