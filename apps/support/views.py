from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            
            try:
                send_mail(
                    subject=f'New Help Ticket: {ticket.subject}',
                    message=f'From: {ticket.name} ({ticket.email})\n\nMessage:\n{ticket.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
            return redirect('support:contact_success')
    
    return redirect('/')


def contact_success(request):
    return render(request, 'support/contact_page_landing.html')