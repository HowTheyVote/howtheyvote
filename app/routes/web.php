<?php

use App\Http\Controllers\HomeController;
use App\Http\Controllers\MembersController;
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

Route::get('/', [HomeController::class, 'index'])->name('home');
Route::get('/about', fn () => view('about'));
Route::get('/imprint', fn () => view('imprint'));

Route::get('/monitoring', [MonitoringController::class, 'index'])->name('monitoring.index');
Route::get('/monitoring/lists/{votingList}', [MonitoringController::class, 'showLists'])->name('monitoring.showLists');
Route::get('/monitoring/votes/{vote}', [MonitoringController::class, 'showVotes'])->name('monitoring.showVotes');

Route::get('/votes', [VotingListsController::class, 'index'])->name('voting-lists.index');
Route::get('/votes/{votingList}.csv', [VotingListsController::class, 'csv'])->name('voting-list.csv');
Route::get('/votes/{votingList}', [VotingListsController::class, 'show'])->name('voting-list.show');
Route::get('/votes/{votingList}/summary', [VotingListsController::class, 'summary'])->name('voting-list.summary');
Route::get('/votes/{votingList}/related', [VotingListsController::class, 'related'])->name('voting-list.related');

Route::get('/votes/{votingList}/share-picture', [VotingListsController::class, 'sharePicture'])->name('voting-list.share-picture');

Route::get('/members/{member}', [MembersController::class, 'show'])->name('members.show');
// Handles short URLs and should be registered as the last route
Route::get('/{hashId}', [VotingListsController::class, 'short'])->name('voting-list.short');
