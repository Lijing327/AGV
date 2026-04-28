package com.seer.sdk.rbk;

import io.netty.buffer.ByteBuf;
import io.netty.buffer.ByteBufUtil;
import io.netty.channel.ChannelFuture;
import io.netty.channel.EventLoopGroup;
import lombok.Builder;
import lombok.Data;

import java.util.concurrent.TimeUnit;

@Data
@Builder
class NettyClient {
    private EventLoopGroup eventLoopGroup;
    private ChannelFuture channelFuture;

    public void write(ByteBuf bf) throws InterruptedException {
        ByteBufUtil.prettyHexDump(bf);
        channelFuture.channel().writeAndFlush(bf).await(5000, TimeUnit.MILLISECONDS);
    }

/**
 * 关闭方法，用于释放网络资源
 * 该方法会依次关闭channel、等待channel关闭完成、以及关闭事件循环组
 */
    public void close() {
        try {
        // 关闭channel
            channelFuture.channel().close();
        // 同步等待channel关闭完成
            channelFuture.channel().closeFuture().sync();
        } catch (InterruptedException e) {
            // ignore
        } finally {
            try {
                eventLoopGroup.shutdownGracefully().sync();
            } catch (InterruptedException e) {
                // ignore
            }
        }
    }
}
