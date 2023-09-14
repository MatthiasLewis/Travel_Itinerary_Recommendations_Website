from marshmallow import Schema, fields

# Schema
class travelPostSchema(Schema):
    county = fields.Str(example="台北市",required=True)
    dates = fields.Int(example=2)
    departure_date = fields.Str(example="2023-07-24")
    return_date = fields.Str(example="2023-07-25")
    
    hotel_level = fields.Int(example=5)
    food_level = fields.Int(example=5)
    viewpoint_level = fields.Int(example=5)

    viewpoint_other_tag = fields.List(fields.String(),example=["戶外活動","海洋"])
    transportation = fields.Int(example=1)

    food_taste_tag = fields.List(fields.String(),example=["火鍋"])
    food_price_tag = fields.Int(example=2)
    food_other_tag = fields.List(fields.String(),example=["親子餐廳"])
    
    hotel_price_tag = fields.Int(example=5000)
    hotel_like_tag = fields.List(fields.String(),example=["民宿"])
    hotel_other_tag = fields.List(fields.String(),example=["停車場"])

# Response
class travelPostResponse(Schema):
    message = fields.Str(example="success")
    datatime = fields.Str(example="1970-01-01T00:00:00.000000")
    data = fields.Dict()
