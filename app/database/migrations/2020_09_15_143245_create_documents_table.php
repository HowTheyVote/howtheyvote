<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateDocumentsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('documents', function (Blueprint $table) {
            $table->id();
            $table->unsignedTinyInteger('type');
            $table->foreignId('term_id')->constrained();
            $table->unsignedSmallInteger('number');
            $table->year('year');
            $table->string('title')->nullable();
            $table->timestamps();

            $table->unique(['type', 'term_id', 'number', 'year']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('documents');
    }
}
