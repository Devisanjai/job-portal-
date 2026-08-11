5. **Create the PostgreSQL database**
```sql
   CREATE DATABASE deploynix_db;
```

6. **Run migrations**
```bash
   python manage.py migrate
```

7. **Create a superuser** (for Django admin access)
```bash
   python manage.py createsuperuser
```

8. **Run the development server**
```bash
   python manage.py runserver
```

   Visit `http://127.0.0.1:8000`

### Running tests

```bash
python manage.py test
```

---

## Project structure