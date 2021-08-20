<?php

use Illuminate\Database\Migrations\Migration;

class FillFinalCollumnOnVotesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        $collections = DB::select('select * from vote_collections');

        foreach ($collections as $collection) {
            $finalVote = DB::table('votes')
                ->select('id')
                ->where('vote_collection_id', $collection->id)
                ->orderByDesc('id')
                ->take(1)
                ->get();

            DB::update('update votes set final = 1 where id = ?', [$finalVote]);
        }
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
