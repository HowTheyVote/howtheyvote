<?php

namespace App\Http\Controllers;

use Spatie\Sheets\Facades\Sheets;

class PagesController extends Controller
{
    public function show(string $slug)
    {
        $page = Sheets::collection('pages')->get($slug);

        if (! $page) {
            return abort(404);
        }

        return view('pages.show', ['page' => $page]);
    }
}
