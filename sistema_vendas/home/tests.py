from django.test import TestCase
from django.test import Client
from .logic import validarLogin

# Create your tests here.
class loginTestCase(TestCase):
    formLoginCorrect: dict[str:str] = {}
    formLoginIncorrect: dict[str:str] = {}

    def setUp(self):
        self.formLoginCorrect['email'] = "admin@admin.com"
        self.formLoginCorrect['senha'] = "admin"

        self.formLoginIncorrect['email'] = "qualquer@email.com"
        self.formLoginIncorrect['senha'] = "senhaErrada"
    
    def test_login_sucesso(self):
        """ teste da função de login """
        print(self.formLoginCorrect)
        self.assertEqual(validarLogin(self.formLoginCorrect), True)

    def test_login_falha(self):
        """ teste de falha na função de login """
        print(self.formLoginIncorrect)
        self.assertEqual(validarLogin(self.formLoginIncorrect), False)

class LoginPathTestCase(TestCase):
    cliente = Client()
    response_get: any
    response_post: any

    def setUp(self):
        formLogin: dict[str:str] = {}
        formLogin['email'] = "admin@admin.com"
        formLogin['senha'] = "admin"

        self.response_get = self.cliente.get("/login/")
        self.response_post = self.cliente.post("/login/", formLogin)

    def test_login_get(self):
        """" teste de método get da rota da página de login """
        print(self.response_get)
        self.assertEqual(self.response_get.status_code, 200)
    
    def test_login_post(self):
        """ teste de método post da rota da página de login """
        print(self.response_post)
        self.assertEqual(self.response_post.status_code, 302)