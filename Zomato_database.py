import json
import mysql.connector


def send_to_db(extracted):
#Mysql Connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
    )
    cursor = conn.cursor()

    cursor.execute("create database if not exists zomato_db")
    cursor.execute("USE zomato_db")
    #Restaurant table
    create_res_query = """
            CREATE TABLE IF NOT EXISTS zomato_Restaurant(
            RestaurantId int primary key,
            RestaurantName varchar(20),
            RestaurantUrl varchar(500),
            FssaiNo JSON,
            Address TEXT,
            City TEXT,
            Pincode JSON,
            Cuisine JSON,
            Timing JSON
    
          );
    """
    cursor.execute(create_res_query)

    res = []
    res.append((
        extracted["restaurant_id"],
        extracted["restaurant_name"],
        extracted["restaurant_url"],
        json.dumps(extracted["fssai_licence_number"]),
        extracted["address_info"]["full_address"],
        extracted["address_info"]["city"],
        extracted["address_info"]["pincode"],
        json.dumps(extracted["cuisines"]),
        json.dumps(extracted["timings"]),
    ))
    #insert values
    insert_res_query = """
            insert into zomato_Restaurant(
                RestaurantId, RestaurantName,RestaurantUrl,FssaiNo,Address,City,Pincode,Cuisine,Timing 
            )VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(insert_res_query, res)

    #Menu Table
    create_menu_query = """
            CREATE TABLE IF NOT EXISTS zomato_menu(
            SrNo int auto_increment primary key,
            ItemId VARCHAR(100) ,
            RestaurantId int,
            ItemName VARCHAR(50),
            Category varchar(50),
            Description varchar(100),
            IsVeg boolean,
            ItemSlug text,
            FOREIGN KEY (RestaurantId) REFERENCES zomato_Restaurant(RestaurantId)
        );
    """
    cursor.execute(create_menu_query)
    res_id=extracted["restaurant_id"]
    row = []
    dtaa = extracted["menu_categories"]
    for category in dtaa:
        name = category["category_name"]
        for item in category["items"]:
            row.append((
                item["item_id"],
                res_id,
                item["item_name"],
                name,
                item.get("item_description"),
                item.get("is_veg"),
                ",".join(item.get("item_slug", []))
            ))
    #insert values
    insert_query = """
            insert into zomato_menu(
                ItemId,restaurantId,ItemName,Category,Description,IsVeg,ItemSlug
            )VALUES(%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(insert_query, row)
    conn.commit()