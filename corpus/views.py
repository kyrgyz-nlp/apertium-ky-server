from django.shortcuts import render, get_object_or_404, redirect
from .models import Text, UnknownWord, UnknownWordBatch, VersionedText
from django.http import JsonResponse
import subprocess

def run_apertium_command(input_text):
    command = f'echo "{input_text}" | apertium -d /home/app/apertium-kir kir-seg'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def extract_base_words(segmented_text):
    words = segmented_text.strip().split()
    known_words = []
    unknown_words = []

    for word in words:
        if '*' in word:
            base_form = word.replace('*', '')
            unknown_words.append(base_form)
        else:
            base_form = word.split('>')[0]
            known_words.append(base_form)

    return known_words, unknown_words

def find_word_positions(text, word):
    positions = []
    start = 0
    while start < len(text):
        start = text.find(word, start)
        if start == -1:
            break
        end = start + len(word)
        positions.append({"start": start, "end": end})
        start += len(word)
    return positions

def process_text(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    if text.status == 'Uploaded':
        text.status = 'Processing'
        text.save()
        
        segmented_text = run_apertium_command(text.content)
        known_words, unknown_words = extract_base_words(segmented_text)
        
        unknown_word_objs = []
        for word in unknown_words:
            positions = find_word_positions(text.content, word)
            unknown_word_objs.append(UnknownWord(word=word, text=text, context=text.content, positions=positions))
        
        UnknownWord.objects.bulk_create(unknown_word_objs)
        
        unknown_word_batch = UnknownWordBatch.objects.create(text=text)
        unknown_word_batch.words.set(unknown_word_objs)
        unknown_word_batch.status = 'Pending'
        unknown_word_batch.save()

        text.status = 'Cleaned'
        text.save()

        response_data = {
            "known": known_words,
            "unknown": unknown_words
        }
        return JsonResponse(response_data)
    return JsonResponse({"error": "Invalid status"}, status=400)

def check_unknown_words(request, batch_id):
    batch = get_object_or_404(UnknownWordBatch, id=batch_id)
    if batch.status == 'Pending':
        for word in batch.words.all():
            if word.word in ['example_typo']:  # Replace with actual checking logic
                word.is_typo = True
                word.correct_form = 'correct_form_example'
            else:
                word.is_valid = True
            word.save()

        batch.status = 'Checked'
        batch.save()
        return JsonResponse({"status": "Checked"})
    return JsonResponse({"error": "Invalid status"}, status=400)

def update_apertium(request, batch_id):
    batch = get_object_or_404(UnknownWordBatch, id=batch_id)
    if batch.status == 'Checked':
        batch.status = 'UpdatingApertium'
        batch.save()
        
        # Perform Apertium update process
        # Update Apertium dictionary with valid words
        
        batch.status = 'RebuildingApertium'
        batch.save()
        
        subprocess.run(["make"], cwd="/home/app/apertium-kir")
        
        batch.status = 'Rechecking'
        batch.save()
        
        text = batch.text
        segmented_text = run_apertium_command(text.content)
        known_words, unknown_words = extract_base_words(segmented_text)
        
        batch.words.clear()
        for word in unknown_words:
            unknown_word = UnknownWord.objects.filter(word=word, text=text).first()
            if unknown_word:
                batch.words.add(unknown_word)

        if not batch.words.exists():
            batch.status = 'Completed'
            create_new_versioned_text(text, known_words)
        batch.save()
        
        return JsonResponse({"status": batch.status})
    return JsonResponse({"error": "Invalid status"}, status=400)

def create_new_versioned_text(text, known_words):
    try:
        latest_version = VersionedText.objects.filter(text=text).order_by('-version_number').first()
        new_version_number = latest_version.version_number + 1 if latest_version else 1
    except VersionedText.DoesNotExist:
        new_version_number = 1

    updated_content = text.content
    for word in known_words:
        unknown_word = UnknownWord.objects.filter(word=word, text=text).first()
        if unknown_word and unknown_word.is_typo and unknown_word.correct_form:
            updated_content = updated_content.replace(unknown_word.word, unknown_word.correct_form)

    VersionedText.objects.create(
        text=text,
        version_number=new_version_number,
        updated_content=updated_content
    )

def upload_text(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        date = request.POST['date']
        source = request.POST['source']
        content = request.POST['content']
        text = Text.objects.create(
            title=title,
            author=author,
            date=date,
            source=source,
            content=content,
            status='Uploaded'
        )
        return redirect('text_detail', text_id=text.id)
    return render(request, 'upload_text.html')

def text_detail(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    return render(request, 'text_detail.html', {'text': text})
