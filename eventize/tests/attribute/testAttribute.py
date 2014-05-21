from .. import TestCase, Mock
from eventize import Attribute, handle, on_get, on_set, on_del, on_change
from eventize.events import Expect

class ClassWithAttribute(object):
    attribute = None

class AttributeTest(TestCase):
    def setUp(self):
        self.obj = ClassWithAttribute()
        handle(self.obj, 'attribute').clear_all()


    def test_setting_Attribute_store_value_in_instance_dict(self):
        self.obj.attribute = 'value'

        self.assertEqual('value', self.obj.__dict__['attribute'].data)
        self.assertIsInstance(self.obj.__class__.attribute, Attribute)

    def test_can_delete_attribute(self):
        self.obj.attribute = 'value'
        del self.obj.attribute
        self.assertFalse(hasattr(self.obj, 'attribute'))

    def test_if_attribute_not_set_expect_AttributeError(self):
        with self.assertRaises(AttributeError):
            self.obj.attribute

    def test_not_set_attribute_returns_default_if_set(self):
        expected = 'default'
        class test(object):
            attribute = Attribute(expected)

        obj = test()

        self.assertEqual(obj.attribute, expected)

    def test_can_observe_get_event(self):
        event = Mock()
        get_attr = on_get(ClassWithAttribute, 'attribute').do(event)
        self.obj.attribute = "value"
        getattr(self.obj, 'attribute')

        event.assert_called_once_with(get_attr.events[0])

    def test_can_observe_get_event_on_object(self):
        event = Mock()
        self.obj.attribute = "value"
        get_attr = on_get(self.obj, 'attribute')
        get_attr += event

        getattr(self.obj, 'attribute')
        event.assert_called_once_with(get_attr.events[0])

    def test_can_observe_set_event(self):
        event = Mock()
        set_attr = on_set(ClassWithAttribute, 'attribute').do(event)

        setattr(self.obj, 'attribute', "value")

        event.assert_called_once_with(set_attr.events[0])

    def test_can_observe_del_event(self):
        event = Mock()
        del_attr = on_del(ClassWithAttribute, 'attribute').do(event)
        self.obj.attribute = "value"

        del self.obj.attribute
        event.assert_called_once_with(del_attr.events[0])

    def test_when_setting_different_value_on_change_is_triggered(self):
        event = Mock()
        change = on_change(ClassWithAttribute, 'attribute').do(event)
        self.obj.attribute = "value"

        event.assert_called_once_with(change.events[0])

    def test_when_setting_same_value_on_change_is_not_triggered(self):
        event = Mock()
        change = on_change(ClassWithAttribute, 'attribute').do(event)
        self.obj.attribute = "value"
        self.obj.attribute = "value"

        event.assert_called_once_with(change.events[0])


    def test_can_observe_get_event_for_a_given_instance(self):
        event = Mock()
        obj1 = ClassWithAttribute()
        obj1.attribute = "value"
        obj2 = ClassWithAttribute()
        obj2.attribute = "value"
        obj3 = ClassWithAttribute()
        obj3.attribute = "value"

        condition = Expect.subject(obj1) | Expect.subject(obj3)
        on_get(ClassWithAttribute, 'attribute').when(condition).do(event)

        getattr(obj1, 'attribute', None)
        getattr(obj2, 'attribute', None)
        getattr(obj3, 'attribute', None)

        self.assertEqual(2, event.call_count)

    def test_can_observe_set_event_for_a_given_instance(self):
        event = Mock()
        value = "value"

        set_attr = on_set(self.obj, 'attribute').do(event)

        self.obj.attribute = value
        event.assert_called_once_with(set_attr.events[0])

    def test_can_use_when_on_handle(self):
        event = Mock()
        expected = "value"
        value_is_expected = Expect.value(expected)

        set_attr = handle(self.obj, 'attribute')
        set_attr.when(value_is_expected).on_set_class += event

        self.obj.attribute = expected
        self.obj.attribute = ""
        event.assert_called_once_with(set_attr.on_set.events[0])


    def test_can_observe_set_event_for_a_given_value(self):
        event = Mock()
        value = "value"
        expect_value = Expect.value(value)

        set_attr = on_set(ClassWithAttribute, 'attribute')
        set_attr.when(expect_value).do(event)

        self.obj.attribute = "foo"
        self.obj.attribute = value
        self.obj.attribute = "bar"
        self.assertEqual(1, event.call_count)

    def test_can_observe_del_event_for_a_given_instance(self):
        event = Mock()
        self.obj.attribute = "value"
        expected = self.obj.attribute

        del_attr = on_del(self.obj, 'attribute').do(event)

        delattr(self.obj, 'attribute')
        event.assert_called_once_with(del_attr.events[0])

    def test_it_add_events_attributes_to_instance_value(self):
        self.obj.attribute = "value"
        events = handle(self.obj, 'attribute')

        att_items = dir(ClassWithAttribute.attribute.get(self.obj, 'attribute'))

        self.assertIn('on_get', att_items)
        self.assertIn('on_set', att_items)
        self.assertIn('on_del', att_items)

    def test_on_get_value_event_is_triggered_only_for_given_instance(self):
        event = Mock()
        obj1 = ClassWithAttribute()
        obj2 = ClassWithAttribute()
        obj1.attribute = "value"
        obj2.attribute = "value"

        on_get(obj1, 'attribute').do(event)
        on_get(obj2, 'attribute').do(event)

        getattr(obj1, 'attribute')

        self.assertEqual(1, event.call_count)

    def test_on_set_value_event_is_triggered_only_for_given_instance(self):
        event = Mock()
        obj1 = ClassWithAttribute()
        obj2 = ClassWithAttribute()
        obj1.attribute = "value"
        obj2.attribute = "value"

        on_set(obj1, 'attribute').do(event)
        on_set(obj2, 'attribute').do(event)

        obj1.attribute = "value1"

        self.assertEqual(1, event.call_count)

    def test_on_del_value_event_is_triggered_only_for_given_instance(self):
        event = Mock()
        obj1 = ClassWithAttribute()
        obj2 = ClassWithAttribute()
        obj1.attribute = "value"
        obj2.attribute = "value"

        on_del(obj1, 'attribute').do(event)
        on_del(obj2, 'attribute').do(event)

        del obj1.attribute

        self.assertEqual(1, event.call_count)


    def test_on_del_events_are_kept(self):
        event = Mock()
        self.obj.attribute = "value"
        expected = on_del(self.obj, 'attribute').do(event)
        del self.obj.attribute

        self.assertIs(on_del(self.obj, 'attribute'), expected)


    def test_value_events_preserve_object_class_and_contents(self):
        class MyClass(object):
            attr = 10

        obj1 = ClassWithAttribute()
        obj2 = MyClass()
        obj2.attr = 20

        obj1.attribute = obj2

        self.assertEqual(20, obj1.attribute.attr)
        self.assertEqual(MyClass, obj1.attribute.__class__)


    def test_value_events_preserve_types(self):
        self.obj.attribute = 30

        self.assertIsInstance(self.obj.attribute, type(30))

    def test_can_set_a_boolean_as_default(self):
        class TestDefault(object):
            default = Attribute(False)

        obj = TestDefault()
        self.assertFalse(obj.default)

    def test_non_overridable_types_are_observable_throught_class_called_with(self):
        class TestDefault(object):
            default = Attribute(True)

        event = Mock()
        value_is_true = Expect.value(True)

        get_attr = on_get(TestDefault, 'default').when(value_is_true).do(event)
        obj = TestDefault()
        self.assertTrue(obj.default)

        event.assert_called_once_with(get_attr.events[0])

    def test_can_observe_events_within_kwarg_instance_type(self):
        class TestDefault(object):
            default = Attribute(True)

        event = Mock()
        value_is_instance_of_true = Expect.value.instance_of(bool)

        set_attr = on_set(TestDefault, 'default')
        set_attr.when(value_is_instance_of_true).do(event)
        obj = TestDefault()
        obj.default = False

        event.assert_called_once_with(set_attr.events[0])

    def test_can_observe_events_within_kwarg_type(self):
        class TestDefault(object):
            default = Attribute(True)

        event = Mock()
        value_type_is_object = Expect.value.type_is(object)

        set_attr = on_set(TestDefault, 'default')
        set_attr.when(value_type_is_object).do(event)
        obj = TestDefault()
        obj.default = list([1, 2, 3])
        obj.default = object()

        event.assert_called_once_with(set_attr.events[1])

    def test_can_observe_get_event_at_Attribute_level(self):
        event = Mock()
        Attribute.on_get += event
        self.obj.attribute = "value"

        getattr(self.obj, 'attribute')

        event.assert_called_once_with(Attribute.on_get.events[0])
