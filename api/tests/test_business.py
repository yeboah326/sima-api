from api.users.models import User
from api.business.models import Business
from api.product.models import Product
from api.tests.test_utils import (
    create_business_products,
    create_new_business,
    create_business_salelist,
    create_business_stocklist,
    login_user,
)


def test_business_hello(app, client):
    response = client.get("/business/hello")
    assert response.status_code == 200

def test_business_create_new(app, client):
    login = login_user(app, client)

    response = client.post(
        "/business",
        json={"name": "Kako Inc", "description":"Very cool business"},
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    created_business = Business.query.filter_by(name="Kako Inc")

    assert response.status_code == 201
    assert response.json["message"] == "New business successfully created"


def test_business_get_all(app, client):
    # Login user
    login = login_user(app, client)

    create_new_business(client, login["token"])

    # Get all products
    response = client.get(
        "/business", headers={"Authorization": f"Bearer {login['token']}"}
    )

    current_user = User.query.filter_by(public_id=login["public_id"]).first()

    assert response.status_code == 200
    assert len(response.json) == 1

# TODO: Fix issue with test
def test_business_get_by_id(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()

    response = client.get(
        f"/business/{new_business.id}",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json == {"description": "Very cool business", "name": "Kako Inc"}


def test_business_update_by_id(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    id = new_business.id

    # Update the business
    response = client.put(
        f"/business/{new_business.id}",
        json={"name": "Kako Inc II"},
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    new_business_updated = Business.query.filter_by(id=id).first()

    assert response.status_code == 200
    assert response.json == {"message": "User info updated successfully"}
    assert new_business_updated.name == "Kako Inc II"


def test_business_delete_all(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    # Delete all user businesses
    response = client.delete(
        "/business", headers={"Authorization": f"Bearer {login['token']}"}
    )

    assert response.status_code == 200
    assert response.json == {"message": "Businesses deleted successfully"}


def test_business_delete_by_id(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    id = new_business.id

    # Delete business by id
    response = client.delete(
        f"/business/{new_business.id}",
        json={"name": "Kako Inc II"},
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Business deleted"}
    assert Business.query.filter_by(id=id).first() == None


def test_business_create_new_product(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    id = new_business.id

    response = client.post(
        f"/business/{id}/product",
        json={
            "name": "Product 1",
            "business_id": id,
            "description": "Latest model of the business",
        },
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 201
    assert response.json == {"message": "Product created successfully"}


def test_business_get_all_product(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    id = new_business.id

    create_business_products(client, login["token"], id)

    response = client.get(
        f"business/{id}/product", headers={"Authorization": f"Bearer {login['token']}"}
    )

    assert response.status_code == 200
    assert len(response.json) == 2
    assert "description" in response.json[0]
    assert "name" in response.json[0]
    assert "product_id" in response.json[0]


# Sale and SaleList
def test_business_get_all_sale_list(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new salelist
    create_business_salelist(client, login["token"], product_id)

    response = client.get(
        f"business/{business_id}/sale_list?items_per_page=2&page=1",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert "business" in response.json
    assert "business_sale_lists" in response.json
    assert len(response.json["business_sale_lists"]) == 1


def test_business_delete_all_sale_list(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    create_business_salelist(client, login["token"], product_id)

    response = client.delete(
        f"business/{business_id}/sale_list",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "message": f"All salelist from {Business.query.filter_by(id=business_id).first().name} have been deleted"
    }


# Stock and StockList
def test_business_get_all_stock_list(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new stocklist
    for _ in range(10):
        create_business_stocklist(client, login["token"], product_id)

    response = client.get(
        f"business/{business_id}/stock_list?items_per_page=2&page=1",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert "business" in response.json
    assert "business_stock_lists" in response.json
    assert len(response.json["business_stock_lists"]) == 2
    assert "total_quantity" in response.json["business_stock_lists"][0]
    assert "total_buying_price" in response.json["business_stock_lists"][0]


def test_business_delete_all_stock_list(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new stocklist
    create_business_stocklist(client, login["token"], product_id)

    response = client.delete(
        f"business/{business_id}/stock_list",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "message": f"All stocklist from {Business.query.filter_by(id=business_id).first().name} have been deleted"
    }

# Customer
# TODO: Fix issue with test
def test_business_get_all_customers(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new salelist
    create_business_salelist(client, login["token"], product_id)

    response = client.get(
        f"business/{business_id}/customers",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json["business_customers"][0]["customer_name"] == "Kojo Boateng"
    assert response.json["business_customers"][0]["customer_contact"] == "0543217725"

def test_business_get_report(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new stocklist
    for _ in range(10):
        create_business_stocklist(client, login["token"], product_id)
        create_business_salelist(client, login["token"], product_id)

    response = client.get(
        f"business/{business_id}/report",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json["total_sales_made"] == 2900.0
    assert response.json["total_stock_purchased"] == 3000.0
    assert response.json["total_products_sold"] == 180
    assert response.json["total_products_bought"] == 200
    assert response.json["total_products_remaining"] == 20

# TODO: Write test for business_get_dashboard_info endpoint
def test_business_get_dashboard_info(app, client):
    login = login_user(app, client)

    create_new_business(client, login["token"])

    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create a new sstocklist
    create_business_stocklist(client, login["token"], product_id)

    # Create a new salelist
    create_business_salelist(client, login["token"], product_id)

    response = client.get(
        f"business/{business_id}/dashboard_info",
        headers={"Authorization": f"Bearer {login['token']}"}
    )
    print(response.json)
    assert response.status_code == 200
    assert response.json["product_low_on_stock"] == {'Product 0': {'total_items_remaining': '0', 'total_sales_quantity': "0", 'total_stock_quantity': "0"}, 'Product 1': {'total_items_remaining': '2', 'total_sales_quantity': 18, 'total_stock_quantity': 20}}
    assert response.json["top_selling_products"] == {'Product 0': {'total_sales_money': 0, 'total_sales_quantity': '0'}, 'Product 1': {'total_sales_money': 290.00, 'total_sales_quantity': '"18"'}}