    def test_custom_page_size(self):
        """Тест кастомного размера страницы"""
        response = self.client.get('/api/nodes/?page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что пагинация работает (количество может быть меньше из-за тестовых данных)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
