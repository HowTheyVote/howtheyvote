<?php

use App\Http\Controllers\MonitoringController;
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

Route::get('/monitoring', [MonitoringController::class, 'index'])->name('monitoring.index');

Route::get('/votes/{votingList}.csv', [VotingListsController::class, 'csv'])->name('voting-list.csv');
Route::get('/votes/{votingList}', [VotingListsController::class, 'show'])->name('voting-list.show');
Route::get('/votes/{votingList}/related', [VotingListsController::class, 'related'])->name('voting-list.related');

Route::get('/votes/{votingList}/share-picture', [VotingListsController::class, 'sharePicture'])->name('voting-list.share-picture');

// Handles short URLs and should be registered as the last route
Route::get('/{hashId}', fn ($hashId) => null)->name('voting-list.short');
