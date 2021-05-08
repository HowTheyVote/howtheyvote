<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class RecreateVotesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('votes', function (Blueprint $table) {
            $table->id();
            $table->timestamps();
            $table->string('subject')->nullable();
            $table->string('author')->nullable();
            $table->unsignedSmallInteger('result');
            $table->unsignedSmallInteger('type');
            $table->unsignedSmallInteger('split_part')->nullable();
            $table->string('amendment')->nullable();
        });

        Schema::table('voting_lists', function (Blueprint $table) {
            $table->foreignId('vote_id')->nullable()->constrained();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('votes');
    }
}
