from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository:
    def init(self):
        self.data = {}

    def add(self, item):
        if not hasattr(item, 'id'):
            raise ValueError("Item must have an 'id' attribute")
        print(f"Adding item with ID: {item.id}")  # Debug
        self.data[item.id] = item

    def get(self, item_id):
        print(f"Looking for item with ID: {item_id}")  # Debug
        return self.data.get(item_id)

    def get_by_attribute(self, attr, value):
        for item in self.data.values():
            if getattr(item, attr) == value:
                return item
        return None

    def update(self, item):
        if item.id in self.data:
            print(f"Updating item with ID: {item.id}")  # Debug
            self.data[item.id] = item
            return True
        print(f"Item with ID {item.id} not found")  # Debug
        return False

    def get_all(self):
        print(f"Current data in repository: {self.data}")  # Debug
        return list(self.data.values())
