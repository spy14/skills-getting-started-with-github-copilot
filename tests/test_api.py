import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_module(module):
    # snapshot activities so tests don't leave persistent changes
    module._activities_backup = copy.deepcopy(activities)


def teardown_module(module):
    # restore activities to original state
    activities.clear()
    activities.update(module._activities_backup)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # signup should succeed
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # signing up again for same email should fail (400)
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # unregister should succeed
    r3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregistering again should return 404
    r4 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r4.status_code == 404
