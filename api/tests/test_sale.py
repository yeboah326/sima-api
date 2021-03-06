from api.business.models import Business
from api.product.models import Product
from api.sale.models import Sale, SaleList
from api.tests.test_utils import (
    create_business_products,
    create_new_business,
    create_business_salelist,
    login_user,
)


def test_sale_hello(app, client):
    response = client.get("/sale/hello")
    assert response.status_code == 200
    assert response.json == {"message": "Sale blueprint working"}

# TODO: Fix issue with test
def test_sale_get_all_by_sale_list_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id

    response = client.get(
        f"sale/sale_list/{salelist_id}?items_per_page=2&page=1",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert len(response.json) == 2


def test_sale_get_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id
    sale_id = Sale.query.filter_by(sale_list_id=salelist_id).first().id

    response = client.get(
        f"sale/{sale_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert "product" in response.json
    assert len(response.json) == 5


def test_sale_delete_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id
    sale_id = Sale.query.filter_by(sale_list_id=salelist_id).first().id

    response = client.delete(
        f"sale/{sale_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    assert response.status_code == 200
    assert response.json == {"message": "Sale deleted successfully"}


def test_sale_update_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id
    sale_id = Sale.query.filter_by(sale_list_id=salelist_id).first().id

    response = client.put(
        f"sale/{sale_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
        json={"quantity": "7"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Sale of product updated successfully"}


def test_sale_add_new_sale_to_salelist(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist = SaleList.query.filter_by(business_id=business_id).first()

    assert len(salelist.sales) == 3

    data = {
        "sales": [
            {"quantity": 5, "selling_price": 15.0, "product_id": product_id},
            {"quantity": 6, "selling_price": 16.0, "product_id": product_id},
            {"quantity": 7, "selling_price": 17.0, "product_id": product_id},
        ]
    }

    response = client.post(
        f"sale/add/{salelist.id}",
        json=data,
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    # Retrieve salelist id for created salelist after adding new sale
    salelist = SaleList.query.filter_by(business_id=business_id).first()

    print(response.json)
    assert response.status_code == 201
    assert response.json == {"message": "New sale added successfully"}
    assert len(salelist.sales) == 6


def test_sale_list_create_new(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id

    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    data = {
        "business_id": Product.query.filter_by(id=product_id).first().business_id,
        "customer_details": {"customer_name": "None", "customer_contact": "0543217725"},
        "sale_list": [
            {"quantity": 5, "selling_price": 15.0, "product_id": product_id},
            {"quantity": 6, "selling_price": 16.0, "product_id": product_id},
            {"quantity": 7, "selling_price": 17.0, "product_id": product_id},
        ],
    }

    response = client.post(
        "sale/list",
        json=data,
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 201
    assert response.json == {"message": "Sale created successfully"}


def test_sale_list_get_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id
    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id

    response = client.get(
        f"sale/list/{salelist_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    print(response.json)
    assert response.status_code == 200
    assert len(response.json) == 6
    assert "id" in response.json
    assert "customer_name" in response.json
    assert "customer_contact" in response.json


def test_sale_list_delete_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id
    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id

    response = client.delete(
        f"sale/list/{salelist_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Sale list deleted successfully"}


def test_sale_list_update_by_id(app, client):
    # Login the user
    login = login_user(app, client)

    # Create a new buiness
    create_new_business(client, login["token"])

    # Retrieve the new business created
    new_business = Business.query.filter_by(name="Kako Inc").first()
    business_id = new_business.id
    # Create products for business
    create_business_products(client, login["token"], business_id)

    # Retrive created product
    new_product = Product.query.filter_by(name="Product 1").first()
    product_id = new_product.id

    # Create business sale_list
    create_business_salelist(client, login["token"], product_id)

    # Retrieve salelist id for created salelist
    salelist_id = SaleList.query.filter_by(business_id=business_id).first().id

    response = client.put(
        f"sale/list/{salelist_id}",
        headers={"Authorization": f"Bearer {login['token']}"},
        json={"customer_name": "Ama"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Sale list updated sucessfully"}
