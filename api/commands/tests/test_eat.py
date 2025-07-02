from datetime import datetime

from api.commands import eat


def test_get_place_detail():
    place_info = {
        "business_status": "OPERATIONAL",
        "geometry": {
            "location": {"lat": 24.7876683, "lng": 120.9976131},
            "viewport": {
                "northeast": {
                    "lat": 24.7889031802915,
                    "lng": 120.9989432802915,
                },
                "southwest": {
                    "lat": 24.7862052197085,
                    "lng": 120.9962453197085,
                },
            },
        },
        "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png",
        "icon_background_color": "#FF9E67",
        "icon_mask_base_uri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
        "name": "\u5c0f\u6728\u5c4b\u9b06\u9905 \u4ea4\u5927\u5e97",
        "opening_hours": {"open_now": True},
        "photos": [
            {
                "height": 720,
                "html_attributions": [
                    '<a href="https://maps.google.com/maps/contrib/117393490480894096487">\u5c0f\u6728\u5c4b\u9b06\u9905 \u4ea4\u5927\u5e97</a>'
                ],
                "photo_reference": "AVzFdbmEd8y4Xxzv1wODSM039rKcUCGoorjbrD42E1qIvgNBH5uv6oOuHQGxLotBemDEzpldO8L6wFBEsVKMtoO17Ef9jO2vFnFmUvEWgFxbhb3xTijlZNeg5X320_sGkgKqmUrFbX4j33_hWy8AEzLj_iLb-vdrT00uFbu7nvjpnFnrGOZc5hLslGVj",
                "width": 1280,
            }
        ],
        "place_id": "ChIJixrR5xE2aDQRcSR1SqrnbRs",
        "plus_code": {
            "compound_code": "QXQX+32 \u53f0\u7063\u65b0\u7af9\u5e02\u6771\u5340\u5149\u660e\u91cc",
            "global_code": "7QP2QXQX+32",
        },
        "price_level": 1,
        "rating": 4.4,
        "reference": "ChIJixrR5xE2aDQRcSR1SqrnbRs",
        "scope": "GOOGLE",
        "types": [
            "restaurant",
            "food",
            "point_of_interest",
            "establishment",
        ],
        "user_ratings_total": 2745,
        "vicinity": "\u6771\u5340\u5927\u5b78\u8def1001\u865f\u4ea4\u901a\u5927\u5b78\u8cc7\u8a0a\u6280\u8853\u670d\u52d9\u4e2d\u5fc3\u524d\u9910\u4ead",
    }
    user_lat = str(24.7876683)
    user_lng = str(120.9976131)
    place_detail = eat.get_place_detail(
        user_lat, user_lng, place_info
    )
    assert place_detail == {
        "name": "小木屋鬆餅 交大店",
        "address": "東區大學路1001號交通大學資訊技術服務中心前餐亭",
        "distance": "0.0 m",
        "rating": 4.4,
        "user_ratings_total": 2745,
        "map_url": "https://www.google.com/maps/search/?api=1&query=24.7876683%2C120.9976131&query_place_id=ChIJixrR5xE2aDQRcSR1SqrnbRs",
    }


class TestGoogleMapSession:
    def test_init(self):
        session = eat.GoogleMapSession()
        assert (datetime.now() - session.last_update_time).days >= 1

    def test_update_time(self):
        session = eat.GoogleMapSession()
        session.update_time()
        assert (
            datetime.now() - session.last_update_time
        ).seconds < 10

    def test_is_expired(self):
        session = eat.GoogleMapSession()
        assert session.is_expired() is True

        session.update_time()
        assert session.is_expired() is False

    def test_set_expired(self):
        session = eat.GoogleMapSession()
        session.update_time()
        session.set_expired()
        assert session.is_expired() is True


def test_print_help(snapshot):
    help_message = eat.print_help()
    assert snapshot == help_message


def test_handle_message_eat():
    msg = eat.handle_message("eat start")
    assert msg == eat.MESSAGE.START_REPLY.value

    msg = eat.handle_message("eat stop")
    assert msg == eat.MESSAGE.STOP_REPLY.value

    msg = eat.handle_message("eat help")
    assert msg == eat.print_help()

    assert eat.handle_message("eat help aaa") == eat.handle_message(
        "eat aaa help"
    )
