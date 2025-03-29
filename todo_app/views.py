from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q

from .models import Task
from .forms import TaskForm, RegisterForm


@login_required
def task_list(request):
    query = request.GET.get('q')
    priority_filter = request.GET.get('priority')

    tasks = Task.objects.filter(user=request.user)

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if priority_filter and priority_filter != "All":
        tasks = tasks.filter(priority=priority_filter)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = tasks.filter(completed=False).count()

    context = {
        'tasks': tasks.order_by('due_date'),
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'query': query,
        'priority_filter': priority_filter,
    }

    return render(request, 'todo_app/task_list.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todo_app/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, "Task updated successfully.")
        return redirect('task_list')
    return render(request, 'todo_app/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect('task_list')
    return render(request, 'todo_app/task_confirm_delete.html', {'task': task})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created 🎉')
            return redirect('task_list')
        else:
            messages.error(request, 'Something went wrong. Please check the form.')
    else:
        form = RegisterForm()
    return render(request, 'todo_app/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Please check your username and password.")
        return super().form_invalid(form)
    

@login_required
def profile_view(request):
    return render(request, 'todo_app/profile.html')

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('login')
    return render(request, 'todo_app/delete_account.html')


