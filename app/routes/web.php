<?php

use App\Http\Controllers\HomeController;
use App\Http\Controllers\MembersController;
use App\Http\Controllers\MonitoringController;
use App\Http\Controllers\PagesController;
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

Route::get('/', [HomeController::class, 'index'])->name('home');

Route::get('/pages/{slug}', [PagesController::class, 'show'])->name('pages.show');

Route::controller(MonitoringController::class)->group(function () {
    Route::get('/monitoring', 'index')->name('monitoring.index');
    Route::get('/monitoring/lists/{votingList}', 'showLists')->name('monitoring.showLists');
    Route::get('/monitoring/votes/{vote}', 'showVotes')->name('monitoring.showVotes');
});

Route::controller(VotingListsController::class)->group(function () {
    Route::get('/votes', 'index')->name('voting-lists.index');
    Route::get('/votes/{votingList}.csv', 'csv')->name('voting-list.csv');
    Route::get('/votes/{votingList}.json', 'json')->name('voting-list.json');
    Route::get('/votes/{votingList}', 'show')->name('voting-list.show');
    Route::get('/votes/{votingList}/summary', 'summary')->name('voting-list.summary');
    Route::get('/votes/{votingList}/related', 'related')->name('voting-list.related');
    Route::get('/votes/{votingList}/share-picture', 'sharePicture')->name('voting-list.share-picture');
});

Route::get('/members/{member}', [MembersController::class, 'show'])->name('members.show');
// Handles short URLs and should be registered as the last route
Route::get('/{hashId}', [VotingListsController::class, 'short'])->name('voting-list.short');
