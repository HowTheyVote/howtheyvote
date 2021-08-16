<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class IncreaseTitleLengthTo512CharsInVoteCollectionsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('vote_collections', function (Blueprint $table) {
            // MariaDB needs an index on foreign key columns. In order to drop
            // the unique index that contains the `term_id` we first need to
            // create another temporary index for that column.
            $table->index('term_id');
            $table->dropUnique('vote_collections_term_id_date_title_unique');
        });

        Schema::table('vote_collections', function (Blueprint $table) {
            $table->string('title', 512)->change();

            // Recreate the unique index
            $table->unique(['term_id', 'date', 'title']);

            // Drop the temporary index
            $table->dropUnique('vote_collections_term_id_index');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        //
    }
}
