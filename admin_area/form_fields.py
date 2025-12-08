"""
Custom form fields for Flask-Admin with image upload support
"""
from wtforms import FileField, TextAreaField
from wtforms.widgets import html_params, TextArea
try:
    from markupsafe import Markup
except ImportError:
    from flask import Markup


class ImageUploadField(FileField):
    """
    Custom file upload field that replaces URL input with file selector
    and shows image preview on edit pages
    """
    
    def __init__(self, label=None, validators=None, image_url_field=None, **kwargs):
        super(ImageUploadField, self).__init__(label, validators, **kwargs)
        self.image_url_field = image_url_field
        self.current_url = None
    
    def __call__(self, **kwargs):
        """Render the field with file input and preview"""
        kwargs.setdefault('id', self.id)
        kwargs.setdefault('type', 'file')
        kwargs.setdefault('accept', 'image/*')
        
        # Add CSS class for styling
        classes = kwargs.get('class', '').split() if 'class' in kwargs else []
        classes.extend(['image-upload-field', 'form-control'])
        kwargs['class'] = ' '.join(classes)
        
        # Build file input
        file_input = f'<input {html_params(name=self.name, **kwargs)}>'
        
        # Get current image URL if editing (set by form)
        preview_html = ''
        if self.current_url:
            preview_html = f'''
            <div class="image-preview-container" style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 4px; border: 1px solid #dee2e6;">
                <label style="display: block; margin-bottom: 10px; font-weight: bold; color: #495057;">تصویر فعلی:</label>
                <img src="{self.current_url}" alt="Current Image" 
                     style="max-width: 300px; max-height: 200px; border: 1px solid #ced4da; border-radius: 4px; padding: 5px; background: #fff; display: block;"
                     onerror="this.style.display='none';">
                <p style="margin-top: 10px; color: #6c757d; font-size: 13px; margin-bottom: 0;">
                    برای تغییر تصویر، فایل جدیدی انتخاب کنید
                </p>
            </div>
            '''
        
        # Build help text
        help_text = '''
        <small class="form-text text-muted" style="margin-top: 5px; display: block;">
            فرمت‌های مجاز: PNG, JPG, JPEG, GIF, WEBP, SVG (حداکثر 10MB)
        </small>
        '''
        
        return Markup(f'<div class="image-upload-wrapper">{file_input}{preview_html}{help_text}</div>')


class CKEditorTextAreaWidget(TextArea):
    """Custom widget that renders a textarea with CKEditor"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        kwargs.setdefault('class', 'ckeditor')
        
        # Build textarea
        textarea = f'<textarea {html_params(**kwargs)}>{field._value() or ""}</textarea>'
        
        # Add CKEditor initialization script
        ckeditor_script = f'''
        <script>
        (function() {{
            function initCKEditor() {{
                if (typeof CKEDITOR !== 'undefined') {{
                    CKEDITOR.replace('{field.id}', {{
                        language: 'fa',
                        contentsLangDirection: 'rtl',
                        height: 400,
                        filebrowserBrowseUrl: '',
                        filebrowserUploadUrl: ''
                    }});
                }} else {{
                    setTimeout(initCKEditor, 100);
                }}
            }}
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initCKEditor);
            }} else {{
                initCKEditor();
            }}
        }})();
        </script>
        '''
        
        return Markup(f'{textarea}{ckeditor_script}')


class CKEditorField(TextAreaField):
    """TextAreaField with CKEditor widget"""
    widget = CKEditorTextAreaWidget()
