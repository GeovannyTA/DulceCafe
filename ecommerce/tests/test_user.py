import pytest
from django.contrib.auth.models import User
from ecommerce.models import Questions, Answers, Customer, Product

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def customer(user):
    return Customer.objects.create(user=user, name='Test Customer', email='test@example.com')

@pytest.fixture
def product():
    return Product.objects.create(name='Test Product', price=10.99, digital=False)

@pytest.fixture
def question():
    return Questions.objects.create(titulo_pregunta='Test Question')

@pytest.fixture
def answer(question):
    return Answers.objects.create(pregunta=question, respuesta_pregunta='Test Answer')

@pytest.mark.django_db
def test_user_creation(user):
    assert isinstance(user, User)
    assert user.username == 'testuser'
    assert user.check_password('testpassword')

@pytest.mark.django_db
def test_customer_creation(customer, user):
    assert isinstance(customer, Customer)
    assert str(customer) == 'Test Customer'
    assert customer.name == 'Test Customer'
    assert customer.email == 'test@example.com'
    assert customer.user == user

@pytest.mark.django_db
def test_product_creation(product):
    assert isinstance(product, Product)
    assert str(product) == 'Test Product'
    assert product.name == 'Test Product'
    assert product.price == 10.99

@pytest.mark.django_db
def test_question_creation(question):
    assert isinstance(question, Questions)
    assert str(question) == 'Test Question'
    assert question.titulo_pregunta == 'Test Question'

@pytest.mark.django_db
def test_answer_creation(answer, question):
    assert isinstance(answer, Answers)
    assert str(answer) == 'Test Answer'
    assert answer.respuesta_pregunta == 'Test Answer'
    assert answer.pregunta == question