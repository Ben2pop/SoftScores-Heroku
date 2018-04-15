import pytest
from mixer.backend.django import mixer
import mock 
from pytest_mock import mocker
pytestmark = pytest.mark.django_db


class TestGetExplanation:

    def test_getNewUser(self):
        usr = mixer.blend('registration.MyUser')
        prj = mixer.blend('website.Project', project_hr_admin=usr)
        assert usr.pk == 1, 'Should create a user'
        assert prj.project_hr_admin.id == 1, 'Should be linked to a user'



class TestInnovationGrade:
    def test_score(self):
        values = mixer.blend('get_compelete_team_scores()')


#Extract score of each user;
#For each user extract ID - 0 -1 - 3 - 5 -12 -14
#create a Ponderation for each model ID
