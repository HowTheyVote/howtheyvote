<?php

namespace App\Http\Controllers;

use App\Session;
use Illuminate\Support\Carbon;

class HomeController extends Controller
{
    public function index()
    {
        $today = Carbon::now();

        $currentSession = Session::query()
            ->where('start_date', '<=', $today)
            ->where('end_date', '>=', $today)
            ->first();

        $lastSession = Session::query()
            ->where('start_date', '<=', $today)
            ->where('end_date', '<', $today)
            ->orderByDesc('start_date')
            ->first();

        $nextSession = Session::query()
            ->where('start_date', '>', $today)
            ->orderBy('start_date')
            ->first();

        return view('home', [
            'currentSession' => $currentSession,
            'lastSession' => $lastSession,
            'nextSession' => $nextSession,
        ]);
    }
}
