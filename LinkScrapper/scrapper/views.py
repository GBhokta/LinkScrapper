import requests
from bs4 import BeautifulSoup
from newspaper import Article
from django.shortcuts import render
from django.http import HttpResponse
from .forms import URLForm
from io import BytesIO
from reportlab.pdfgen import canvas

def scrape_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']

            # Fetch HTML content
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return render(request, 'form.html', {'form': form, 'error': f"Error fetching URL: {e}"})

            # Parse HTML with BeautifulSoup to extract all links and their names
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = [(a.get_text(strip=True), a.get('href')) for a in soup.find_all('a', href=True) if a.get('href')]

            # Uncomment the following block to re-enable working links check
            # working_links = []
            # for name, link in all_links:
            #     try:
            #         link_response = requests.head(link, timeout=5)
            #         if link_response.status_code == 200:
            #             working_links.append((name, link))
            #     except requests.exceptions.RequestException:
            #         continue
            # else:
            #     working_links = all_links  # Use all links without validation

            working_links = all_links  # Skip validation

            # Summarize content using Newspaper3k
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            summary = article.summary

            # Save summary in session for use in download_pdf view
            request.session['summary'] = summary

            # Render result template with all links and summary
            return render(request, 'result.html', {'summary': summary, 'links': working_links})
    else:
        form = URLForm()

    return render(request, 'form.html', {'form': form})

def download_pdf(request):
    # Retrieve the summary from session data
    summary = request.session.get('summary', 'No summary available')

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="summary.pdf"'

    # Create PDF content
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Webpage Summary")
    pdf.drawString(100, 730, "Content Summary:")
    
    # Split the summary text into lines that fit the PDF
    y_position = 710
    for line in summary.splitlines():
        pdf.drawString(100, y_position, line)
        y_position -= 15
        if y_position < 50:  # Move to the next page if content is too long
            pdf.showPage()
            y_position = 750

    pdf.showPage()
    pdf.save()

    # Serve the PDF as an HTTP response
    buffer.seek(0)
    response.write(buffer.read())
    return response
