<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Administration')</title>

    @vite(['resources/css/app.css', 'resources/js/app.js']) {{-- Pour Laravel Breeze/Inertia si utilisé --}}
    @livewireStyles
</head>
<body>

    <nav>
        <ul>
            <li><a href="{{ route('gestion.notes') }}">Gestion des Notes</a></li>
        </ul>
    </nav>

    <div class="container">
        @yield('content')
    </div>

    @livewireScripts
</body>
</html>
