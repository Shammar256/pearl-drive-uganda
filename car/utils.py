from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML


def render_to_pdf(template_src, context_dict=None):
    """Render template → PDF response."""
    context_dict = context_dict or {}
    template = get_template(template_src)
    html = template.render(context_dict)
    pdf_bytes = HTML(string=html, base_url="").write_pdf()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="report.pdf"'
    return response