class DishMemory:
    """Класс для хранения последних предложенных блюд и избежания повторов"""
    
    def __init__(self, max_dishes=5):
        self.max_dishes = max_dishes
        self.recent_dishes = {
            "завтрак": [],
            "обед": [],
            "ужин": []
        }
    
    def add_dish(self, meal_type, dish_name):
        """Добавить блюдо в память"""
        print(f"[MEMORY DEBUG] Добавляем блюдо '{dish_name}' в категорию '{meal_type}'")
        if meal_type in self.recent_dishes:
            self.recent_dishes[meal_type].append(dish_name)
            # Оставляем только последние max_dishes блюд
            if len(self.recent_dishes[meal_type]) > self.max_dishes:
                removed = self.recent_dishes[meal_type].pop(0)
                print(f"[MEMORY DEBUG] Удалили старое блюдо: '{removed}'")
            print(f"[MEMORY DEBUG] Текущая память для {meal_type}: {self.recent_dishes[meal_type]}")
        else:
            print(f"[MEMORY ERROR] Неизвестная категория: {meal_type}")
    
    def get_recent_dishes(self, meal_type):
        """Получить список последних блюд для категории"""
        return self.recent_dishes.get(meal_type, [])
    
    def clear_old(self, meal_type=None):
        """Очистить старые блюда (для конкретной категории или всех)"""
        if meal_type and meal_type in self.recent_dishes:
            self.recent_dishes[meal_type] = []
        elif meal_type is None:
            for category in self.recent_dishes:
                self.recent_dishes[category] = []
    
    def get_avoid_list_text(self, meal_type):
        """Получить текст для промпта с блюдами для избежания"""
        recent = self.get_recent_dishes(meal_type)
        if recent:
            return f"НЕ предлагай эти блюда (уже были недавно): {', '.join(recent)}."
        return ""

# Глобальный экземпляр памяти
dish_memory = DishMemory()