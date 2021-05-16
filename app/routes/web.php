<?php

use App\Http\Controllers\VotingListsController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::get('/', function () {
    return view('welcome');
});

Route::get('/votes/{votingList}/share-picture', [VotingListsController::class, 'sharePicture'])->name('voting-list.share-picture');
Route::get('/{hashId}', fn ($hashId) => null)->name('voting-list.short');
