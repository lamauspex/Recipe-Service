@field_validator('user_name')
 @classmethod
  def validate_user_name(cls, v):
       if not v or len(v.strip()) < 3:
            raise ValueError(
                'Имя пользователя должно содержать минимум 3 символа'
            )

        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Имя пользователя может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )
        return v.strip()
