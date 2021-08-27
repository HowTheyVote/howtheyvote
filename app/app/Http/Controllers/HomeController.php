<?php

namespace App\Http\Controllers;

use App\Session;

class HomeController extends Controller
{
    public function index()
    {
        return view('home', [
            'currentSession' => Session::current(),
            'lastSession' => Session::last(),
            'nextSession' => Session::next(),
        ]);
    }
}
